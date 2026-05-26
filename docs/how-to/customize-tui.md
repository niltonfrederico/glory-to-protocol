<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="customize-tui.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# How-to: Customize the Textual TUI

The Textual surface ships with a NIRVYTEKH bureau identity. Consumers swap or extend
that identity through `BureauTheme`, `LayoutSettings`, and the `app_factory`
injection point on the `Protocol` facade.

## Recipe 1 — Swap identity (logo, name, colors)

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

The header logo, footer labels, help-as-directive overlay, and accent borders all
rebase onto the new theme.

## Recipe 2 — Override keybinds

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

The active mapping shows up in the help overlay's bindings table, so operators see
exactly what's bound without reading code.

## Recipe 3 — Subclass `ProtocolApp` for a custom screen

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
            yield Static("All systems nominal.")

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

The subclass inherits the header/body/footer composition, the palette/form dispatch,
and the result stamp pipeline — you only add what's new.

## Recipe 4 — Hide the result stamp

```python
settings = ProtocolSettings(layout=LayoutSettings(show_result_stamp=False))
```

The dispatch still runs; the stamp render after the callback is skipped.

## Recipe 5 — Theme via env vars

```bash
export PROTOCOL_LAYOUT__BUREAU__NAME=PROTON
export PROTOCOL_LAYOUT__BUREAU__ACCENT='#00a886'
export PROTOCOL_LAYOUT__BUREAU__LOGO_TEXT=PROTON
export PROTOCOL_LAYOUT__LOGO_SIZE=large
uv run protocol-tui
```

Pydantic-settings reads nested fields through `__`. The same pattern works for any
field on `BureauTheme` or `LayoutSettings`.
