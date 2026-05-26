<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="quickstart.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Quickstart

Dez minutos do `pip install` até uma CLI que renderiza a moldura do bureau,
imprime um stamp, e acompanha um job em background. Sem precisar conhecer
Typer ou Rich — você aprende o necessário no caminho.

No fim você vai ter um comando `archive` que:

1. Abre a moldura do bureau com o header de logo grande.
2. Imprime uma linha de status.
3. Roda um job "sync" falso em background com ticker ao vivo.
4. Imprime um stamp `APPROVED` ou `REJECTED` baseado no outcome.

## Pré-requisitos

- Python 3.14.
- Diretório limpo e virtualenv. `uv venv && source .venv/bin/activate.fish`
  resolve.

## 1. Instale a lib

```bash
pip install glory-to-protocol
```

Ou, com `uv`:

```bash
uv add glory-to-protocol
```

## 2. Bootstrap do arquivo

Crie `bureau.py`:

```python
import typer
from glory_to_protocol import configure, make_app

configure(
    app_name="MyBureau",
    logo_text="MyBureau",
    small_logo_text="MyBureau",
)

app = make_app()
```

`configure(**overrides)` é o ponto canônico de acoplamento entre a sua CLI e a
lib — muta o singleton de settings. `make_app()` retorna um `typer.Typer()`
pré-ligado com o renderer de `--help` do bureau.

Rode uma vez pra confirmar:

```bash
python bureau.py --help
```

Você deve ver o banner de help em dourado. Se quebrar com
`InvalidASCIICharactersError`, você passou um caractere fora do alfabeto ASCII
default no `logo_text` — só A–Z maiúsculo e dígitos.

## 3. Primeiro comando com Form

Adicione:

```python
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui import theme

@app.command()
def status() -> None:
    """Imprime o status atual do bureau."""
    with Form(title="status") as form:
        form.line("Todos os sistemas nominais.", style=theme.BODY)
        form.line("Diretor de plantão.", style=theme.MUTED)
```

Rode:

```bash
python bureau.py status
```

Você deve ver a moldura do bureau, o header de logo, duas linhas de corpo, e o
rodapé com assinatura.

## 4. Imprimir um stamp

Stamps são as decisões terminais do bureau. Adicione:

```python
from glory_to_protocol.tui.stamps import stamp_approve, stamp_reject

@app.command()
def review(reject: bool = False) -> None:
    """Finge revisar um pedido e carimba."""
    with Form(title="review") as form:
        form.line("Examinando pedido #4711...", style=theme.MUTED)
        if reject:
            form.stamp(stamp_reject("pedido #4711", "fora do escopo"))
        else:
            form.stamp(stamp_approve("pedido #4711", "auditoria limpa"))
```

```bash
python bureau.py review            # APPROVED
python bureau.py review --reject   # REJECTED
```

## 5. Rodar um job em background

A lib vem com um runner assíncrono que renderiza ticker ao vivo. Adicione:

```python
import asyncio
from glory_to_protocol.jobs.types import Job

async def fake_sync() -> None:
    await asyncio.sleep(2)

@app.command()
def archive() -> None:
    """Arquiva as entradas do ledger do dia."""
    with Form(title="archive") as form:
        form.line("Reconciliando com o arquivo central...", style=theme.MUTED)
        outcomes = asyncio.run(
            form.run_pending([
                Job(label="sincronizando ledger", coro_factory=fake_sync),
            ])
        )

    failed = any(o.status == "fail" for o in outcomes)
    with Form(title="archive · resultado", show_header=False) as form:
        if failed:
            form.stamp(stamp_reject("archive", "sync falhou"))
        else:
            form.stamp(stamp_approve("archive", "ledger reconciliado"))
```

Note duas coisas:

- `coro_factory=fake_sync` passa a **função**, não o resultado. O runner chama
  a factory quando faz spawn do job. Passar `fake_sync()` ligaria a coroutine
  ao event loop errado. Veja
  [reference/jobs.pt-br.md#por-que-uma-factory](../reference/jobs.pt-br.md#por-que-uma-factory).
- O segundo `Form` usa `show_header=False` pra você não ter um bloco de logo
  duplicado na moldura de resultado.

Rode:

```bash
python bureau.py archive
```

Você deve ver a primeira moldura abrir, ticker contando dois segundos, e a
segunda moldura com um stamp `APPROVED`.

## 6. Pluga como console script

Mova `bureau.py` pra um package e adicione no `pyproject.toml`:

```toml
[project.scripts]
my-bureau = "my_package.bureau:app"
```

Agora `my-bureau status`, `my-bureau review`, `my-bureau archive` são comandos
de verdade no seu ambiente.

## Próximos passos

- **A superfície interativa** — envolva `app` numa facade `Protocol` com
  `Mode.HYBRID` e adicione `@expose` nos seus comandos. Rodar sem argumentos
  abre a paleta Textual fullscreen (j/k pra navegar, `?` pro help-as-despacho,
  `ctrl+\` pra command palette nativa). Veja
  [reference/textual.pt-br.md](../reference/textual.pt-br.md) e
  [how-to/customize-tui.pt-br.md](../how-to/customize-tui.pt-br.md).
- **Branding custom** — mude logo, diretor, assinatura, e stamps via
  `configure()`; troque a identidade Textual via `BureauTheme`. Veja
  [reference/settings.pt-br.md](../reference/settings.pt-br.md).
- **Mais componentes** — `theme.HEADER`, `theme.CYRILLIC_ACCENT`, wrap,
  rollback de pipeline. Veja [reference/components.pt-br.md](../reference/components.pt-br.md)
  e [reference/jobs.pt-br.md](../reference/jobs.pt-br.md).
