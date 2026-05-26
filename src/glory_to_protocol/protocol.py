from __future__ import annotations

import importlib.util
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any
from typing import TextIO

import click
import typer
from rich.console import Console

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.registry import discover_exposed
from glory_to_protocol.settings import Fallback
from glory_to_protocol.settings import Mode
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui._schema import fields_from_typer
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.fallback import degraded_palette
from glory_to_protocol.tui.fallback import prompt_form
from glory_to_protocol.tui.fallback import render_header_oneshot
from glory_to_protocol.tui.screens.result import render_result_stamp


class ProtocolUnavailable(RuntimeError):
    """Raised when the requested mode cannot be served and fallback is 'error'."""


@dataclass(frozen=True, slots=True)
class CapabilityReport:
    ok: bool
    reason: str | None


def _terminal_size() -> tuple[int, int]:
    try:
        size = os.get_terminal_size()
    except OSError:
        return (0, 0)
    return (size.columns, size.lines)


def _textual_importable() -> bool:
    return importlib.util.find_spec("textual") is not None


AppFactory = Callable[["Protocol"], "ProtocolApp"]


class Protocol:
    """Public facade. Owns settings + registry; dispatches to Typer or TUI."""

    def __init__(
        self,
        *,
        typer_app: typer.Typer,
        settings: ProtocolSettings | None = None,
        app_factory: AppFactory | None = None,
    ) -> None:
        self.typer_app = typer_app
        self.settings = settings or ProtocolSettings()
        self.exposed: list[ExposedCommand] = discover_exposed(typer_app)
        self._app_factory: AppFactory = app_factory or ProtocolApp

    @cached_property
    def cli(self) -> click.Command:
        """The underlying click command tree."""
        return typer.main.get_command(self.typer_app)

    def run(
        self,
        argv: list[str] | None = None,
        *,
        console: Console | None = None,
        stdin: TextIO | None = None,
    ) -> None:
        argv = sys.argv[1:] if argv is None else argv
        mode = self.settings.mode

        if mode is Mode.CLI:
            self._dispatch_cli(argv)
            return

        if mode is Mode.HYBRID and argv:
            self._dispatch_cli(argv)
            return

        report = self._capability_check()
        if report.ok:
            self._dispatch_textual()
            return

        if self.settings.fallback is Fallback.ERROR:
            raise ProtocolUnavailable(report.reason or "tui unavailable")

        self._dispatch_fallback(console=console, stdin=stdin)

    def _dispatch_textual(self) -> None:
        app = self._app_factory(self)
        result = app.run()
        if result is None:
            return
        callback, kwargs = result
        outcome = self._invoke_callback(callback, kwargs)
        if self.settings.layout.show_result_stamp:
            command = next((c for c in self.exposed if c.callback is callback), None)
            if command is not None:
                render_result_stamp(command, outcome)

    @staticmethod
    def _invoke_callback(callback: Callable[..., Any], kwargs: dict[str, Any]) -> str:
        try:
            callback(**kwargs)
        except Exception:
            return "rejected"
        return "approved"

    def _dispatch_fallback(
        self,
        *,
        console: Console | None,
        stdin: TextIO | None,
    ) -> None:
        if not self.exposed:
            raise ProtocolUnavailable("no exposed commands available for fallback dispatch")
        active_console = console or Console(highlight=False, soft_wrap=False)
        render_header_oneshot(console=active_console)
        chosen = degraded_palette(self.exposed, console=active_console, stdin=stdin)
        cli_command = self.cli
        if not isinstance(cli_command, click.Group):
            raise ProtocolUnavailable("Typer app did not resolve to a click.Group")
        click_cmd = cli_command.commands.get(chosen.typer_name)
        if click_cmd is None:
            raise ProtocolUnavailable(f"command '{chosen.typer_name}' not registered on Typer app")
        fields = fields_from_typer(click_cmd)
        values = prompt_form(fields, console=active_console, stdin=stdin)
        chosen.callback(**values)

    def _capability_check(self) -> CapabilityReport:
        if not (sys.stdout.isatty() and sys.stdin.isatty()):
            return CapabilityReport(False, "stdio is not a tty")
        if not _textual_importable():
            return CapabilityReport(False, "textual package is not installed")
        cols, lines = _terminal_size()
        v = self.settings.viewport
        if cols < v.min_width or lines < v.min_height:
            return CapabilityReport(
                False,
                f"terminal too small (need {v.min_width}×{v.min_height}, have {cols}×{lines})",
            )
        return CapabilityReport(True, None)

    def _dispatch_cli(self, argv: list[str]) -> None:
        self.cli.main(args=argv, standalone_mode=True)
