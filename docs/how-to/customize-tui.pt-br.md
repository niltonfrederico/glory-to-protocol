<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="customize-tui.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# How-to: Customizar a TUI Textual

A superfície Textual vem com a identidade NIRVYTEKH default. Consumers trocam ou
estendem essa identidade via `BureauTheme`, `LayoutSettings`, e o injection point
`app_factory` na facade `Protocol`.

## Receita 1 — Trocar identidade (logo, nome, cores)

```python
from glory_to_protocol import (
    BureauTheme,
    LayoutSettings,
    Protocol,
    ProtocolSettings,
)
import typer

app = typer.Typer()

@app.callback()
def _root() -> None: ...

settings = ProtocolSettings(
    layout=LayoutSettings(
        bureau=BureauTheme(
            name="PROTON",
            subtitle="Bureau of Protocol Engineering",
            logo_text="PROTON",
            accent="#00a886",
            gold="#f5d65a",
            sign_off="With honor, PROTON",
        ),
    ),
)

protocol = Protocol(typer_app=app, settings=settings)
protocol.run()
```

O logo do header, labels do footer, overlay help-as-despacho, e as bordas accent
todas migram pro tema novo.

## Receita 2 — Sobrescrever keybinds

```python
settings = ProtocolSettings(
    layout=LayoutSettings(
        keybinds={
            "quit": "ctrl+c",
            "help": "f1",
            "back": "escape",
            "filter": "ctrl+f",
        },
    ),
)
```

O mapping ativo aparece na tabela de bindings do overlay de help, então o operador
vê exatamente o que está bindado sem precisar ler código.

## Receita 3 — Subclassar `ProtocolApp` pra adicionar screen próprio

```python
from glory_to_protocol import Protocol, ProtocolApp
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class HealthOverlay(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss_overlay", "close")]

    def compose(self):
        with Vertical():
            yield Static("Todos os sistemas nominais.")

    def action_dismiss_overlay(self) -> None:
        self.dismiss()


class MyApp(ProtocolApp):
    BINDINGS = ProtocolApp.BINDINGS + [
        Binding("ctrl+h", "open_health", "health", show=False),
    ]

    def action_open_health(self) -> None:
        self.push_screen(HealthOverlay())


protocol = Protocol(typer_app=app, app_factory=MyApp)
```

A subclasse herda a composição header/body/footer, o dispatch palette/form, e o
pipeline do stamp de resultado — você só adiciona o que é novo.

## Receita 4 — Esconder o stamp de resultado

```python
settings = ProtocolSettings(layout=LayoutSettings(show_result_stamp=False))
```

O dispatch continua rodando; só o stamp depois do callback é pulado.

## Receita 5 — Tema via env vars

```bash
export PROTOCOL_LAYOUT__BUREAU__NAME=PROTON
export PROTOCOL_LAYOUT__BUREAU__ACCENT='#00a886'
export PROTOCOL_LAYOUT__BUREAU__LOGO_TEXT=PROTON
export PROTOCOL_LAYOUT__LOGO_SIZE=large
uv run protocol-tui
```

Pydantic-settings lê campos nested via `__`. O mesmo padrão funciona pra qualquer
campo de `BureauTheme` ou `LayoutSettings`.
