<!-- markdownlint-disable MD041 -->

<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/read%20in-english-c0392b?style=for-the-badge" alt="Read in English">
  </a>
</p>

<p align="center">
  <a href="https://github.com/niltonfrederico/glory-to-protocol/actions/workflows/ci.yml"><img src="https://github.com/niltonfrederico/glory-to-protocol/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/glory-to-protocol/"><img src="https://img.shields.io/pypi/v/glory-to-protocol.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/glory-to-protocol/"><img src="https://img.shields.io/pypi/pyversions/glory-to-protocol.svg" alt="Versões de Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licen%C3%A7a-AGPL--3.0--or--later-blue.svg" alt="Licença: AGPL-3.0-or-later"></a>
</p>

<p align="center">
  <img src="assets/svg/header-pt-br.svg" alt="glory-to-protocol — Bureau de Tecnologia Computacional" width="880">
</p>

## СВОДКА · Resumo

Uma biblioteca Python TUI para CLIs em
[Typer](https://typer.tiangolo.com/) que veste seus comandos numa
estética estatal-burocrática sem ironia — formulários emoldurados, quatro
carimbos de decisão (`approve` / `reject` / `order` / `review`), `--help`
tematizado, header com logo ASCII e um ticker ao vivo de jobs em
background. Construída porque ferramentas úteis e ferramentas divertidas
raramente se cruzam.

<p align="center">
  <img src="assets/gifs/showcase.gif" alt="protocol-showcase — todos os componentes TUI renderizados" width="900">
</p>

## ОГЛАВЛЕНИЕ · Sumário

- [СВОДКА · Resumo](#%D1%81%D0%B2%D0%BE%D0%B4%D0%BA%D0%B0--resumo)
- [ОГЛАВЛЕНИЕ · Sumário](#%D0%BE%D0%B3%D0%BB%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5--sum%C3%A1rio)
- [ПОЛЕ № 1 · Propósito](#%D0%BF%D0%BE%D0%BB%D0%B5--1--prop%C3%B3sito)
- [ПОЛЕ № 2 · Instalação](#%D0%BF%D0%BE%D0%BB%D0%B5--2--instala%C3%A7%C3%A3o)
  - [pip](#pip)
  - [uv](#uv)
  - [poetry](#poetry)
- [ПОЛЕ № 3 · Uso](#%D0%BF%D0%BE%D0%BB%D0%B5--3--uso)
  - [Configuração](#configura%C3%A7%C3%A3o)
  - [Integração com Typer CLI](#integra%C3%A7%C3%A3o-com-typer-cli)
  - [Componentes](#componentes)
    - [Form](#form)
    - [Logo](#logo)
    - [Paleta](#paleta)
    - [Wrap](#wrap)
    - [Carimbos](#carimbos)
  - [Jobs em background](#jobs-em-background)
- [ПОЛЕ № 4 · Status & Roteiro](#%D0%BF%D0%BE%D0%BB%D0%B5--4--status--roteiro)
- [ОТКАЗ · Isenção](#%D0%BE%D1%82%D0%BA%D0%B0%D0%B7--isen%C3%A7%C3%A3o)
- [ВКЛАД · Contribuição](CONTRIBUTING.pt-br.md)
  - [Для граждан повышенного допуска · Para cidadãos de alta patente](TRUE_CONTRIBUTING.pt-br.md)
- [КОДЕКС · Código de Conduta](CODE_OF_CONDUCT.pt-br.md)
  - [Для граждан повышенного допуска · Para cidadãos de alta patente](TRUE_CODE_OF_CONDUCT.pt-br.md)
- [ЛИЦЕНЗИЯ · Licença](LICENSE)

## ПОЛЕ № 1 · Propósito

Uma biblioteca Python TUI para CLIs em
[Typer](https://typer.tiangolo.com/) — formulários com bordas
emolduradas, quatro tipos de carimbo de decisão (`approve` / `reject` /
`order` / `review`), um renderizador de `--help` tematizado, header com
logo ASCII e ticker ao vivo de jobs em background. A biblioteca oferece
uma subclasse `ProtocolTyper` e o helper `make_app()` para que a moldura
do bureau apareça em todo comando e sub-app sem fiação extra; veja
[Integração com Typer CLI](#integra%C3%A7%C3%A3o-com-typer-cli) abaixo.

Construí isso porque eu vivia esbarrando em bibliotecas que eram *úteis* ou
*divertidas*, e quase nunca as duas coisas. Queria que minhas próprias CLIs
parecessem um artefato — imprimindo `REJECTED` com timestamp em vez de
`Error: invalid input`. Que ela funcione bem como toolkit TUI no caminho é
efeito colateral.

A estética — acentos cirílicos, títulos de bureau, carimbos sem ironia —
saiu do jeito que saiu porque eu estava mergulhado em Papers, Please na
época. A biblioteca não reusa uma linha de código nem um asset do jogo
(veja a [isenção](#%D0%BE%D1%82%D0%BA%D0%B0%D0%B7--isen%C3%A7%C3%A3o)), mas a vibe é inconfundivelmente da
mesma prateleira.

Uma nota sobre o russo: eu falo alguma coisa, e alguns termos aqui estão
torcidos de propósito pro efeito cômico-burocrático, mas estou longe de ser
falante nativo. Se algo soar acidentalmente errado — ou, pior,
acidentalmente ofensivo — por favor
[abra uma issue](https://github.com/niltonfrederico/glory-to-protocol/issues/new)
e eu corrijo.

## ПОЛЕ № 2 · Instalação

### pip

```bash
pip install glory-to-protocol
```

### uv

```bash
uv add glory-to-protocol
```

### poetry

```bash
poetry add glory-to-protocol
```

## ПОЛЕ № 3 · Uso

### Configuração

A biblioteca expõe um único singleton `ProtocolSettings` que segura toda a
marca de nível bureau. Os defaults renderizam o visual NIRVYTEKH direto da
caixa; sobrescreva-os ao plugar a lib na sua própria CLI.

| Campo | Default | Efeito |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------- |
| `app_name` | `"Protocol"` | Nome genérico do app (usado como fallback). |
| `logo_text` | `"Protocol"` | Texto renderizado como o logo ASCII grande (header). |
| `small_logo_text` | `"Protocol"` | Texto renderizado no logo pequeno emoldurado (carimbos).|
| `bureau_title` | `"БЮРО NIRVYTEKH · Bureau of Computational Technology"` | Subtítulo abaixo do logo grande no header. |
| `director_name` | `"Норман"` | Nome do diretor exibido na meta-linha do header. |
| `director_signature` | `"Подписано: Норман, Директор NIRVYTEKH"` | Linha de assinatura no rodapé do form. |
| `ascii.allowed_alphabet` | maiúsculas A–Z, 0–9 | Caracteres permitidos em `logo_text` / `small_logo_text`.|

`logo_text` é validado contra `ascii.allowed_alphabet` — passar caracteres
fora do conjunto levanta `InvalidASCIICharactersError`.

#### Sobrescrita programática (recomendado)

Use `configure(**overrides)` no startup, antes de qualquer componente
renderizar. Esse é o ponto canônico de acoplamento ao embutir a lib na sua
CLI Typer.

```python
import typer
from glory_to_protocol import configure, make_app

configure(
    app_name="MyBureau",
    logo_text="MyBureau",
    small_logo_text="MyBureau",
    director_name="Ada Lovelace",
    director_signature="Signed: Ada Lovelace, Director",
)

app: typer.Typer = make_app()
```

Cada `configure()` atualiza apenas os campos que você passa; campos não
especificados mantêm o valor. Para testes, `reset_settings()` limpa o
singleton.

### Integração com Typer CLI

A lib oferece uma subclasse `ProtocolTyper` e um helper `make_app()` que
fiam o renderizador de `--help` tematizado em todo comando e sub-app. Veja
[examples/showcase.py](examples/showcase.py) para a referência completa.

```python
import typer
from glory_to_protocol import configure, make_app
from glory_to_protocol.tui.forms import Form

configure(app_name="MyBureau", logo_text="MyBureau", small_logo_text="MyBureau")

app = make_app()


@app.command()
def status() -> None:
    with Form(title="status") as form:
        form.line("All systems nominal.")
```

Pontos de referência em [examples/showcase.py](examples/showcase.py):

- Loop de registro de app + subcomandos Typer:
  [examples/showcase.py:150](examples/showcase.py#L150) e
  [examples/showcase.py:165-173](examples/showcase.py#L165-L173)
- Helper de execução single-shot (Console + Form + save opcional):
  [examples/showcase.py:122](examples/showcase.py#L122)
- Compondo componentes dentro de um Form:
  [examples/showcase.py:109](examples/showcase.py#L109)

### Componentes

#### `Form`

Context manager que desenha a moldura do formulário do bureau (borda
superior, header, divisor, corpo, assinatura, borda inferior). Todo outro
componente renderiza dentro de um `Form`.

```python
from glory_to_protocol.tui.forms import Form

with Form(title="version") as form:
    form.line("Consulting bureau records...")
```

Parâmetros do construtor:

| Parâmetro | Tipo | Default | Propósito |
| ---------------- | ---------------- | ------- | -------------------------------------------------------- |
| `title` | `str` | — | Rótulo da aba na borda superior (ex.: `"version"`). |
| `console` | `Console \| None`| `None` | Injete um `Console` do Rich; criado automaticamente se omitido. |
| `show_header` | `bool` | `True` | Renderiza o bloco com logo grande + título do bureau no topo. |
| `signature_text` | `str \| None` | `None` | Sobrescreve a assinatura do rodapé; default vem das settings. |

Métodos: `line(text, style=None, *, wrap=True)`, `divider()`, `stamp(...)`,
`run_pending(jobs)`.

#### Logo

<p align="center">
  <img src="assets/gifs/showcase-logo.gif" alt="componente de logo" width="900">
</p>

Dois renderizadores de logo ASCII guiados por `logo_text` e
`small_logo_text`:

```python
from glory_to_protocol.tui.logo import logo_large, logo_small

print(logo_large())            # usa settings.logo_text
print(logo_small("ARCHIVE"))   # override explícito
```

Ambos aceitam um `text: str | None` opcional; passar `None` lê as settings
atuais. Os resultados são memoizados — `configure()` invalida o cache.

#### Paleta

<p align="center">
  <img src="assets/gifs/showcase-palette.gif" alt="paleta do tema" width="900">
</p>

O módulo `theme` expõe objetos `Style` nomeados do Rich para tipografia
consistente entre componentes:

```python
from glory_to_protocol.tui import theme

form.line("Default report body.", style=theme.BODY)
form.line("Side note.", style=theme.MUTED)
form.line("Official accent.", style=theme.CYRILLIC_ACCENT)
form.line("Footer signature.", style=theme.SIGNATURE)
```

Outros papéis na paleta: `theme.HEADER`, `theme.BORDER`,
`theme.STAMP_APPROVE`, `theme.STAMP_REJECT`, `theme.STAMP_ORDER`,
`theme.STAMP_REVIEW`.

#### Wrap

<p align="center">
  <img src="assets/gifs/showcase-wrap.gif" alt="comportamento de quebra de linha" width="900">
</p>

`Form.line(text)` quebra por célula até a largura interna do form,
lidando corretamente com conteúdo latino, cirílico e misto. Passe
`wrap=False` para desabilitar a quebra (a linha é truncada para caber):

```python
form.line(long_text)                # default: quebra na largura interna
form.line(long_text, wrap=False)    # trunca em uma linha
```

#### Carimbos

<p align="center">
  <img src="assets/gifs/showcase-stamps.gif" alt="variantes de carimbo" width="900">
</p>

Quatro variantes de carimbo codificam as decisões terminais do bureau sobre
uma solicitação. Cada uma aceita um `label` obrigatório e um `detail`
opcional:

```python
from glory_to_protocol.tui.stamps import (
    stamp_approve, stamp_reject, stamp_order, stamp_review,
)

form.stamp(stamp_approve("Q2 budget", "audit clean"))
form.stamp(stamp_reject("request #4711", "out of bureau scope"))
form.stamp(stamp_order("team 3 mobilization", "immediate execution"))
form.stamp(stamp_review("monthly report", "awaiting Gensek review"))
```

| Variante | Rótulo (RU/EN) | Usar para |
| ---------------- | --------------------------- | ------------------------------------------------------ |
| `stamp_approve` | `ОДОБРЕНО / APPROVED` | Solicitação aceita, ação completa. |
| `stamp_reject` | `ОТКАЗАНО / REJECTED` | Solicitação negada; inclua `detail` com o motivo. |
| `stamp_order` | `ПРИКАЗ / DIRECT ORDER` | Imperativo — o bureau está ditando uma ação. |
| `stamp_review` | `К СВЕДЕНИЮ / FOR REVIEW` | Aguardando decisão externa (ex.: do Gensek). |

Assinatura: `stamp_<variant>(label: str, detail: str = "") -> Table`.

### Jobs em background

<p align="center">
  <img src="assets/gifs/showcase-jobs.gif" alt="região ao vivo de jobs em background" width="900">
</p>

`Form.run_pending(jobs)` dispara uma lista de `Job`s como tasks async e
renderiza um ticker ao vivo até todos atingirem um estado terminal. Falhas
em um job são isoladas — os irmãos continuam rodando.

```python
import asyncio
from glory_to_protocol.jobs.types import Job

async def fetch_quota() -> None:
    await asyncio.sleep(2)

jobs = [
    Job(label="fetching quota", coro_factory=fetch_quota),
    Job(label="archiving ledger", coro_factory=lambda: asyncio.sleep(3)),
]

with Form(title="sync") as form:
    form.line("Reconciling with the bureau...", style=theme.MUTED)
    outcomes = asyncio.run(form.run_pending(jobs))

for outcome in outcomes:
    print(outcome.label, outcome.status, outcome.duration_ms)
```

Campos de `Job`:

| Campo | Tipo | Default | Propósito |
| -------------- | --------------------------------- | ------- | ------------------------------------------------------ |
| `label` | `str` | — | Exibido no ticker ao vivo. |
| `coro_factory` | `Callable[[], Awaitable[None]]` | — | Factory que retorna a coroutine a ser aguardada. |
| `critical` | `bool` | `False` | Só uma tag hoje; reservado para uso futuro de fail-fast.|

`coro_factory` é uma **factory**, não uma coroutine — passar a coroutine
direto a amarraria ao event loop errado. Embrulhe com `lambda` ou um `def`
que retorne o awaitable. Cada job recebe um awaitable fresco no spawn.

Resultados retornados por `run_pending`:

| Campo | Tipo | Significado |
| ------------- | ------------------------------- | ------------------------------------------------ |
| `label` | `str` | Ecoa `Job.label`. |
| `status` | `"ok" \| "fail" \| "skipped"` | Estado terminal. `"skipped"` só é setado pelo `PipelineRunner` em jobs não alcançados. |
| `error` | `BaseException \| None` | A exceção, se `status == "fail"`. |
| `duration_ms` | `int` | Duração em wall-clock do job. |

O runner nunca levanta em falha de job individual; quem chama decide como
um job de background falho afeta o carimbo de foreground.

#### Callbacks (por-job, fan-out)

`JobRunner.spawn` aceita três hooks opcionais por job:

| Kwarg | Dispara quando | Assinatura |
| ------------ | --------------------- | ------------------------------------------ |
| `rollback` | job termina em `fail` | `async (outcome: JobOutcome) -> None` |
| `on_success` | job termina em `ok` | `async (outcome: JobOutcome) -> None` |
| `timeout` | teto wall-clock (s) | `float` |

`rollback` e `on_success` são mutuamente exclusivos na prática — só um roda
por job. Cancelamento pula os dois. Se um callback levanta, o erro é logado
e engolido — não pode mascarar o outcome original nem quebrar o isolamento
entre irmãos.

`timeout` embrulha a coroutine do job em `asyncio.wait_for`; expirado, produz
um outcome `fail` com `TimeoutError`, que então dispara o `rollback` como
qualquer outra falha.

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
```

#### Salvaguardas dos runners

Tanto `JobRunner` quanto `PipelineRunner` aceitam dois kwargs no ctor que
limitam fan-out e protegem contra recursão induzida por callback:

| Kwarg | Default | Efeito |
| -------------- | --------- | ---------------------------------------------------------------------- |
| `max_children` | `12` | Cap em jobs registrados via `spawn`. `0` desabilita (ilimitado). Exceder sempre levanta (bug de programador). |
| `on_recursion` | `"raise"` | `spawn` chamado depois do contexto começar a fechar (ex.: de dentro de um callback) levanta. `"warn"` loga e retorna um handle sintético `"skipped"` não enrolado. |

```python
runner = JobRunner(max_children=0, on_recursion="warn")
```

#### Pipelines (sequencial, transacional)

`PipelineRunner` é a contraparte sequencial do `JobRunner`. Jobs registrados
via `spawn` executam em ordem na saída do contexto; a primeira falha aborta
o pipeline, dispara rollback LIFO dos jobs já completados, marca os não
alcançados como `"skipped"` e re-levanta como `PipelineFailed`.

```python
from glory_to_protocol.jobs import Job, JobOutcome, PipelineFailed, PipelineRunner


async def reserve_quota() -> None: ...
async def write_ledger() -> None: ...
async def notify_director() -> None: ...

async def release_quota(o: JobOutcome) -> None: ...
async def revert_ledger(o: JobOutcome) -> None: ...

try:
    async with PipelineRunner() as p:
        p.spawn(Job("reserve quota", reserve_quota), rollback=release_quota)
        p.spawn(Job("write ledger", write_ledger), rollback=revert_ledger)
        p.spawn(Job("notify director", notify_director))
except PipelineFailed as exc:
    print(exc.failed.label, exc.rolled_back, exc.rollback_errors)
```

Semântica:

- **Ordem.** Jobs rodam na ordem em que foram `spawn`ados.
- **Abort.** Na primeira falha, nenhum job subsequente roda; os handles
  restantes viram `"skipped"`.
- **Rollback LIFO.** Jobs completados com sucesso têm o rollback invocado em
  ordem reversa. Erros de rollback são logados e coletados em
  `PipelineFailed.rollback_errors`; a cadeia continua de qualquer jeito.
- **Falha no primeiro job.** Nada pra desfazer — `rolled_back` vem vazio.
- **Exceção no body.** Se o body do `async with` levanta antes da saída,
  nenhum job roda e a exceção do body propaga sem alteração.

`PipelineFailed` expõe `.failed` (o `JobOutcome` que falhou), `.rolled_back`
(labels revertidos, ordem LIFO) e `.rollback_errors`
(`list[tuple[str, BaseException]]`).

## ПОЛЕ № 4 · Status & Roteiro

**Beta (0.1.1).** A superfície pública — `Form`, os quatro carimbos, `logo_large` / `logo_small`, `theme`, `configure()`, `Job` / `run_pending`, `JobRunner` + `PipelineRunner` (com `rollback`, `on_success`, `timeout`, `max_children` e política `on_recursion`), e `ProtocolTyper` / `make_app` — está estável o suficiente pra dirigir uma CLI real (112 testes, ~98% de cobertura). Versões menores ainda podem refinar APIs antes do 1.0.

Planejado:

- Jobs longos (reporte de progresso, superfície de cancelamento)
- Tracebacks melhores (tematizados, emoldurados dentro do form do bureau)
- Autoria de componentes customizados (API pública de composição)
- Pato de Borracha Senciente (Да, sério)
- TUI interativa

Quer um favor do Верховный Лидер (Líder Supremo)? [Abra uma issue](https://github.com/niltonfrederico/glory-to-protocol/issues/new).

## ОТКАЗ · Isenção

A estética visual e temática deste projeto é vagamente inspirada em
[Papers, Please](https://papersplea.se/) (© Lucas Pope / 3909 LLC),
especificamente sua evocação de um bureau estatal fictício ao estilo do
Bloco do Leste.

A inspiração é apenas atmosférica. **Glory to Protocol não usa, referencia
nem distribui qualquer código, asset, arte, personagem, nome, país ou marca
de Papers, Please.** Nenhum conteúdo de Arstotzka — ou qualquer outro
elemento fictício do jogo — aparece neste repositório. O bureau, sua
nomenclatura, seus símbolos e sua língua são originais deste projeto.

Papers, Please e Arstotzka são propriedade de seus respectivos donos. Este
projeto não é afiliado a, endossado por nem patrocinado por Lucas Pope ou
3909 LLC.

Se a atmosfera deste projeto ressoa com você, considere apoiar o criador
original comprando Papers, Please no
[site oficial](https://papersplea.se/) ou na sua loja preferida. O trabalho
que inspirou essa estética merece ser pago.
