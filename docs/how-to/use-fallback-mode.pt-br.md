<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="use-fallback-mode.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Como usar o modo fallback

Você quer que sua CLI se sinta interativa quando rodada em um terminal de
verdade, e mantenha script-friendly quando piped ou em CI. Esse guia liga a
facade `Protocol` e o caminho Rich pra fazer exatamente isso.

Pro contexto de **por que** o dispatch tem dois eixos (mode + fallback),
veja [explanation/dispatch-modes.pt-br.md](../explanation/dispatch-modes.pt-br.md).

## Pré-requisitos

- Uma Typer app funcionando — qualquer coisa que crie um `typer.Typer()` com
  uma ou mais funções `@app.command()`.
- Um `ProtocolSettings` (ou aceitar os defaults).

## Passo 1 — envolva sua Typer app

Substitua seu entry point pela facade `Protocol`.

```python
import typer
from glory_to_protocol import Mode, Protocol, ProtocolSettings

app = typer.Typer()

@app.command()
def status() -> None:
    print("All systems nominal.")

protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.HYBRID),
)

def main() -> None:
    protocol.run()
```

Plugue `main` como console script no `pyproject.toml`:

```toml
[project.scripts]
my-bureau = "my_package.cli:main"
```

## Passo 2 — escolha o modo de dispatch

`mode` decide o que `Protocol.run()` tenta primeiro.

| `Mode` | Comportamento |
| --- | --- |
| `Mode.CLI` | Sempre Typer. Sem superfície interativa. Use pra binários que precisam ficar headless. |
| `Mode.TUI` | Sempre tenta Textual. Se indisponível, segue `fallback`. |
| `Mode.HYBRID` | Se `argv` nomeia subcommand, Typer. Senão tenta Textual. Default. |

`HYBRID` é o default certo pra maioria: `my-bureau status` continua funcionando,
enquanto `my-bureau` sozinho te leva pra paleta interativa.

```python
ProtocolSettings(mode=Mode.HYBRID)
```

Também dá pra setar pelo ambiente:

```bash
PROTOCOL_MODE=cli my-bureau
```

## Passo 3 — exponha comandos pra paleta

Adicione `@expose` em qualquer comando que você quer listado na paleta. O
decorator vai **acima** de `@app.command()` pro Typer ver o callback envolvido.

```python
from glory_to_protocol import expose

@app.command()
@expose(section="data", icon="◈")
def ingest(path: str, dry_run: bool = False) -> None:
    """Ingerir um arquivo no ledger."""
    ...
```

`expose` lê a primeira linha da docstring como descrição na paleta, e usa o
nome da função (em kebab-case) como label default.

| Kwarg | Efeito |
| --- | --- |
| `label` | Sobrescreve o nome exibido. |
| `section` | Agrupa comandos sob um cabeçalho. |
| `shortcut` | Atalho de teclado (validado contra colisões). |
| `icon` | Ícone de um caractere. |
| `hidden` | Mantém callable pela CLI, omite da paleta. |

Colisões de atalho lançam `ValueError` na construção do `Protocol(...)`.

## Passo 4 — escolha o que acontece quando Textual não roda

`fallback` decide o que `Protocol.run()` faz quando a capability check falha.

| `Fallback` | Efeito |
| --- | --- |
| `Fallback.RICH` | Degrada pra paleta numerada renderizada com Rich + sequência de prompts. |
| `Fallback.ERROR` | Lança `ProtocolUnavailable` com a razão. |

```python
from glory_to_protocol import Fallback, Mode, ProtocolSettings

ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH)
```

A capability check falha quando qualquer uma destas é verdade:

- `sys.stdout` ou `sys.stdin` não é um TTY (piped, CI).
- O pacote `textual` não é importável.
- O terminal é menor que `settings.viewport.min_width × min_height`.

A partir do `0.4.0` a superfície Textual está ao vivo — uma capability check
bem-sucedida abre [`ProtocolApp`](../reference/textual.pt-br.md), não o caminho
Rich. O fallback só engata quando a check recusa (sem TTY, sem `textual`,
terminal pequeno demais).

## Passo 5 — observe o caminho de fallback

Em contexto piped ou CI o dispatcher vai:

1. Imprimir o header do bureau.
2. Listar comandos expostos numerados 1..N.
3. Pedir o índice.
4. Construir uma sequência de prompts a partir dos parâmetros do comando
   (defaults, choices, e strings de `--help` são respeitados).
5. Invocar o callback subjacente com os valores coletados.

Force o fallback localmente piping o binário:

```bash
my-bureau | cat
```

Ou encolhendo o terminal abaixo do floor de viewport configurado.

## Modo estrito pra CI

Use `Fallback.ERROR` em ambientes onde rodar sem TTY deve ser um erro duro:

```python
ProtocolSettings(mode=Mode.TUI, fallback=Fallback.ERROR)
```

Útil pra binários que devem se recusar a rodar sem superfície interativa — o
dispatcher levanta `ProtocolUnavailable` com a razão da falha, que o seu
handler de topo pode transformar em exit code não-zero.

## Juntando tudo

```python
import typer
from glory_to_protocol import (
    Fallback,
    Mode,
    Protocol,
    ProtocolSettings,
    expose,
)

app = typer.Typer()

@app.command()
@expose(section="data", icon="◈")
def ingest(path: str, dry_run: bool = False) -> None:
    """Ingerir um arquivo no ledger."""
    ...

@app.command()
@expose(section="report")
def report() -> None:
    """Imprimir o último relatório do bureau."""
    ...

protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH),
)

def main() -> None:
    protocol.run()
```

- `my-bureau ingest --path foo.csv` → dispatch Typer direto.
- `my-bureau` em terminal → superfície Textual (alt-screen palette + form).
- `my-bureau | cat` → fallback Rich (paleta numerada + prompts).
- Com `Fallback.ERROR`, os dois últimos viram `ProtocolUnavailable`.
