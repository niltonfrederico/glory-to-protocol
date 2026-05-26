<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="jobs.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Jobs

Trabalho em background, emoldurado pelo bureau. Dois runners e alguns tipos de
valor. O atalho `Form.run_pending(jobs)` cobre o caso simples de "fan out e
espera"; os runners dão controle sobre callbacks, timeouts, guard-rails e
rollback de pipeline.

## Tipos de valor

`from glory_to_protocol.jobs import Job, JobOutcome`

### `Job`

```python
@dataclass(frozen=True, slots=True)
class Job:
    label: str
    coro_factory: Callable[[], Awaitable[None]]
    critical: bool = False
```

| Campo | Propósito |
| --- | --- |
| `label` | Mostrado no ticker ao vivo e no `JobOutcome.label` resultante. |
| `coro_factory` | Factory que retorna a coroutine a ser awaited. **Factory, não coroutine.** Veja [Por que uma factory](#por-que-uma-factory). |
| `critical` | Tag-only hoje; reservado pra semântica de fail-fast futura. Permite tagger jobs (audit vs best-effort) sem mudar o schema depois. |

### `JobOutcome`

```python
@dataclass(frozen=True, slots=True)
class JobOutcome:
    label: str
    status: JobStatus
    error: BaseException | None
    duration_ms: int
```

| Campo | Significado |
| --- | --- |
| `label` | Espelha `Job.label`. |
| `status` | `JobStatus.OK` / `JobStatus.FAIL` / `JobStatus.SKIPPED`. `SKIPPED` só é setado pelo `PipelineRunner` em jobs não alcançados. |
| `error` | A exceção, se `status == FAIL`. |
| `duration_ms` | Duração em wall-clock do job. |

`JobStatus` é um `StrEnum` (`"pending"`, `"ok"`, `"fail"`, `"skipped"`) —
comparações com os literais antigos seguem funcionando; código novo deve usar
o enum.

## `Form.run_pending` (atalho)

```python
import asyncio
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui import theme

async def fetch_quota() -> None:
    await asyncio.sleep(2)

jobs = [
    Job(label="buscando cota", coro_factory=fetch_quota),
    Job(label="arquivando ledger", coro_factory=lambda: asyncio.sleep(3)),
]

with Form(title="sync") as form:
    form.line("Reconciliando com o bureau...", style=theme.MUTED)
    outcomes = asyncio.run(form.run_pending(jobs))

for outcome in outcomes:
    print(outcome.label, outcome.status, outcome.duration_ms)
```

`run_pending` faz fan-out dos jobs como async tasks, renderiza ticker ao vivo
até todos chegarem em estado terminal, e retorna os outcomes. Falhas são
isoladas — irmãos seguem rodando. O runner nunca propaga falha individual; o
caller decide como uma falha em background afeta o stamp do foreground.

## `JobRunner`

`from glory_to_protocol.jobs import JobRunner`

Async context manager que faz fan-out de jobs independentes.
Falhas são isoladas.

```python
from glory_to_protocol.jobs import Job, JobOutcome, JobRunner

async def write_temp_file() -> None: ...
async def remove_temp_file(outcome: JobOutcome) -> None: ...
async def audit(outcome: JobOutcome) -> None: ...

async with JobRunner() as runner:
    runner.spawn(
        Job("stage temp file", write_temp_file),
        rollback=remove_temp_file,
        on_success=audit,
        timeout=5.0,
    )

for outcome in runner.outcomes:
    print(outcome.label, outcome.status)
```

### Construtor

| Kwarg | Default | Efeito |
| --- | --- | --- |
| `max_children` | `12` | Limite de jobs registrados via `spawn`. `0` desabilita o limite. Estouro sempre lança (erro de programador). |
| `on_recursion` | `RecursionPolicy.RAISE` | Comportamento quando `spawn` é chamado depois que `__aexit__` começa (ex.: de dentro de callback). |

### `spawn`

```python
def spawn(
    self,
    job: Job,
    *,
    rollback: Callable[[JobOutcome], Awaitable[None]] | None = None,
    on_success: Callable[[JobOutcome], Awaitable[None]] | None = None,
    timeout: float | None = None,
) -> JobHandle:
```

| Kwarg | Dispara quando | Assinatura |
| --- | --- | --- |
| `rollback` | job termina em `FAIL` | `async (outcome: JobOutcome) -> None` |
| `on_success` | job termina em `OK` | `async (outcome: JobOutcome) -> None` |
| `timeout` | limite em wall-clock (segundos) | `float` |

`rollback` e `on_success` são mutuamente exclusivos na prática — só um roda por
job. Cancelamento pula os dois. Se um callback levanta, o erro é logado e
engolido — não mascara o outcome original nem quebra o isolamento entre
irmãos.

`timeout` envolve a coroutine do job em `asyncio.wait_for`; timeout expirado
produz um outcome `FAIL` com `TimeoutError`, que então dispara `rollback` como
qualquer outra falha.

### Cancelamento

Uma task de job que recebe `CancelledError` **não** vira outcome `"fail"`; fica
pending e o `CancelledError` propaga pelo `__aexit__`. Se o corpo do contexto
levanta, tasks pendentes são canceladas antes do `gather`.

## `PipelineRunner`

`from glory_to_protocol.jobs import PipelineRunner, PipelineFailed`

Contraparte sequencial do `JobRunner`. Jobs registrados via `spawn` executam em
ordem no exit do contexto; primeira falha aborta o pipeline, dispara rollback
LIFO dos jobs já completos, marca os não alcançados como `SKIPPED`, e re-lança
como `PipelineFailed`.

```python
from glory_to_protocol.jobs import Job, JobOutcome, PipelineFailed, PipelineRunner

async def reserve_quota() -> None: ...
async def write_ledger() -> None: ...
async def notify_director() -> None: ...

async def release_quota(o: JobOutcome) -> None: ...
async def revert_ledger(o: JobOutcome) -> None: ...

try:
    async with PipelineRunner() as p:
        p.spawn(Job("reservar cota", reserve_quota), rollback=release_quota)
        p.spawn(Job("escrever ledger", write_ledger), rollback=revert_ledger)
        p.spawn(Job("notificar diretor", notify_director))
except PipelineFailed as exc:
    print(exc.failed.label, exc.rolled_back, exc.rollback_errors)
```

### Semântica

| Aspecto | Comportamento |
| --- | --- |
| **Ordem** | Jobs rodam na ordem em que foram `spawn`ed. |
| **Abort** | Primeira falha → nenhum job seguinte roda; handles restantes viram `SKIPPED`. |
| **Rollback LIFO** | Jobs já completos têm seu rollback invocado em ordem inversa. |
| **Erros de rollback** | Logados e coletados em `PipelineFailed.rollback_errors`; a cadeia continua. |
| **Falha no primeiro job** | Nada pra desfazer — `rolled_back` é vazio. |
| **Exceção no corpo** | Se o corpo do `async with` levanta antes do exit, nenhum job roda e a exceção propaga inalterada. |

### `PipelineFailed`

| Atributo | Tipo | Significado |
| --- | --- | --- |
| `failed` | `JobOutcome` | O job que quebrou o pipeline. |
| `rolled_back` | `list[str]` | Labels que rodaram rollback, em ordem LIFO. |
| `rollback_errors` | `list[tuple[str, BaseException]]` | Exceções levantadas por callbacks de rollback. |

Mesmos kwargs de construtor do `JobRunner` (`max_children`, `on_recursion`).

## Guard-rails

Os dois runners compartilham dois kwargs de construtor pra limitar fan-out e
proteger contra recursão induzida por callback:

| Kwarg | Default | Efeito |
| --- | --- | --- |
| `max_children` | `12` | Limite de jobs registrados via `spawn`. `0` desabilita. Estouro sempre lança (erro de programador). |
| `on_recursion` | `RecursionPolicy.RAISE` | `spawn` chamado depois do contexto começar a fechar lança. `WARN` loga e retorna handle sintético `SKIPPED` que não é enrolled. |

```python
from glory_to_protocol.jobs import JobRunner
from glory_to_protocol.jobs.types import RecursionPolicy

runner = JobRunner(max_children=0, on_recursion=RecursionPolicy.WARN)
```

## Por que uma factory?

`coro_factory` retorna uma coroutine a cada chamada — **não é** a coroutine
em si.

```python
# certo
Job(label="fetch", coro_factory=fetch)
Job(label="dormir 3s", coro_factory=lambda: asyncio.sleep(3))

# errado
Job(label="fetch", coro_factory=fetch())               # coroutine ligada ao loop atual
Job(label="dormir 3s", coro_factory=asyncio.sleep(3))
```

Passar a coroutine direto a vincula ao event loop ativo no momento da
construção. Esse loop pode não ser o que o runner usa, e uma coroutine só pode
ser awaited uma vez — o runner respawnando o mesmo `Job` duas vezes daria
runtime error. O contrato de factory deixa cada spawn produzir um awaitable
fresco, vinculado no momento certo.
