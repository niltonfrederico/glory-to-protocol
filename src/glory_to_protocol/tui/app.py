from __future__ import annotations

from typing import TYPE_CHECKING

import click
from textual.app import App
from textual.app import ComposeResult
from textual.binding import Binding

from glory_to_protocol.tui.providers import ExposedCommandProvider
from glory_to_protocol.tui.screens.form import FormScreen
from glory_to_protocol.tui.screens.help import HelpOverlay
from glory_to_protocol.tui.screens.palette import PaletteScreen
from glory_to_protocol.tui.widgets.command_palette import ProtocolCommandPalette
from glory_to_protocol.tui.widgets.footer import BindingsFooter
from glory_to_protocol.tui.widgets.header import OfficialHeader

if TYPE_CHECKING:
    from glory_to_protocol.protocol import Protocol
    from glory_to_protocol.registry import ExposedCommand


_DEFAULT_FOOTER_BINDINGS: list[tuple[str, str]] = [
    ("^q", "quit"),
    ("?", "help"),
    ("/", "filter"),
    ("^\\", "palette"),
    ("enter", "select"),
]


class ProtocolApp(App[tuple]):
    """Root Textual app for the protocol surface.

    Hosts `OfficialHeader` + body + `BindingsFooter`. The body swaps between
    `PaletteScreen` (browse) and `FormScreen` (param input). On submit, the app
    exits with `(callback, kwargs)` so the facade dispatches outside the
    Textual event loop.
    """

    COMMANDS = App.COMMANDS | {ExposedCommandProvider}

    BINDINGS = [
        Binding("question_mark", "open_help", "help", show=False),
    ]

    DEFAULT_CSS = """
    ProtocolApp {
        background: $bg;
    }
    Toast {
        background: $bg;
        color: $text-color;
        border: heavy $accent;
        border-title-color: $gold;
        padding: 1 2;
    }
    Toast .toast--title {
        color: $gold;
        text-style: bold;
    }
    Toast.-information {
        border-left: heavy $accent;
    }
    Toast.-warning {
        border-left: heavy $gold;
    }
    Toast.-error {
        border-left: heavy $accent;
    }
    """

    def __init__(self, protocol: Protocol) -> None:
        self.protocol = protocol
        super().__init__()

    def get_css_variables(self) -> dict[str, str]:
        base = super().get_css_variables()
        theme = self.protocol.settings.layout.bureau
        base.update(
            {
                "accent": theme.accent,
                "gold": theme.gold,
                "bg": theme.bg,
                "border": theme.border,
                "muted": theme.muted,
                "text-color": theme.text_color,
                "bg-tint": theme.bg,
                "background": theme.bg,
                "surface": theme.bg,
                "panel": theme.bg,
                "boost": theme.bg,
                "block-cursor-background": theme.accent,
                "block-cursor-foreground": theme.bg,
                "block-cursor-blurred-background": theme.bg,
                "block-cursor-blurred-foreground": theme.gold,
                "block-cursor-text-style": "bold",
                "block-cursor-blurred-text-style": "bold",
            }
        )
        return base

    def compose(self) -> ComposeResult:
        layout = self.protocol.settings.layout
        yield OfficialHeader(
            layout.bureau,
            layout.logo_size,
            app_name=self.protocol.settings.app_name,
            page="Palette",
        )
        yield PaletteScreen(self.protocol.exposed)
        yield BindingsFooter(layout.bureau, _DEFAULT_FOOTER_BINDINGS)

    def _swap_body(self, new_body: PaletteScreen | FormScreen, page: str) -> None:
        for existing in self.query(PaletteScreen):
            existing.remove()
        for existing in self.query(FormScreen):
            existing.remove()
        header = self.query_one(OfficialHeader)
        header.set_page(page)
        self.mount(new_body, after=header)

    def activate_exposed_command(self, command: ExposedCommand) -> None:
        """Open the FormScreen for the given exposed command (used by provider)."""
        cli = self.protocol.cli
        if not isinstance(cli, click.Group):  # pragma: no cover - defensive
            return
        click_cmd = cli.commands.get(command.typer_name)
        if click_cmd is None:  # pragma: no cover - defensive
            return
        self._swap_body(FormScreen(command, click_cmd), page=command.label)

    def on_palette_screen_selected(self, message: PaletteScreen.Selected) -> None:
        self.activate_exposed_command(message.command)

    def on_form_screen_submitted(self, message: FormScreen.Submitted) -> None:
        self.exit((message.callback, message.kwargs))

    def on_form_screen_cancelled(self, _: FormScreen.Cancelled) -> None:
        self._swap_body(PaletteScreen(self.protocol.exposed), page="Palette")

    def action_open_help(self) -> None:
        layout = self.protocol.settings.layout
        self.push_screen(HelpOverlay(layout.bureau, dict(layout.keybinds)))

    def action_command_palette(self) -> None:
        already_open = self.screen.has_class("--textual-command-palette")
        if self.use_command_palette and not already_open:
            self.push_screen(ProtocolCommandPalette())

    def action_help_quit(self) -> None:
        for key, active_binding in self.active_bindings.items():
            if active_binding.binding.action in ("quit", "app.quit"):
                self.notify(
                    f"Press [b]{key}[/b] to quit the application.",
                    title="Quit?",
                    severity="warning",
                )
                return
