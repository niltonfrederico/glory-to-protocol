from __future__ import annotations

import random

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from glory_to_protocol.tui.identity import BureauTheme


def _format_directive_number() -> str:
    return f"{random.randint(1000, 9999)}"


class HelpOverlay(ModalScreen[None]):
    """Modal help overlay rendered as a directive (despacho oficial).

    The body lists the active bindings; the format frames a help screen as an
    official document. Closed with `escape` or `?`.
    """

    BINDINGS = [
        Binding("escape", "dismiss_overlay", "close", show=False),
        Binding("question_mark", "dismiss_overlay", "close", show=False),
    ]

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
    }
    HelpOverlay #directive {
        width: 70;
        max-height: 80%;
        border: heavy $accent;
        background: $bg;
        padding: 1 2;
    }
    HelpOverlay .directive-head {
        color: $gold;
        text-align: center;
        padding-bottom: 1;
    }
    HelpOverlay .meta-line {
        color: $muted;
    }
    HelpOverlay .body {
        color: $text-color;
        padding: 1 0;
    }
    HelpOverlay .sign-off {
        color: $gold;
        text-align: right;
        padding-top: 1;
    }
    """

    def __init__(self, theme: BureauTheme, bindings: dict[str, str]) -> None:
        super().__init__()
        self._theme = theme
        self._bindings_table = bindings

    def compose(self) -> ComposeResult:
        directive_num = _format_directive_number()
        head = f"{self._theme.directive_prefix} {directive_num}"
        with Vertical(id="directive"):
            yield Static(head, classes="directive-head")
            yield Static(f"FROM: {self._theme.name}", classes="meta-line")
            yield Static("TO:   Operator", classes="meta-line")
            yield Static("RE:   KEYBINDS", classes="meta-line")
            yield Static(self._render_body(), classes="body")
            yield Static(self._theme.sign_off, classes="sign-off")

    def _render_body(self) -> str:
        lines: list[str] = []
        for action, key in self._bindings_table.items():
            label = self._theme.footer_labels.get(action, action)
            lines.append(f"  [{key}]  {label}")
        return "\n".join(lines)

    def action_dismiss_overlay(self) -> None:
        self.dismiss()
