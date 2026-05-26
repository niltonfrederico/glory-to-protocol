from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from functools import cached_property
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
from glory_to_protocol.tui.fallback import degraded_palette
from glory_to_protocol.tui.fallback import prompt_form
from glory_to_protocol.tui.fallback import render_header_oneshot


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


class Protocol:
    """Public facade. Owns settings + registry; dispatches to Typer or TUI."""

    def __init__(
        self,
        *,
        typer_app: typer.Typer,
        settings: ProtocolSettings | None = None,
    ) -> None:
        self.typer_app = typer_app
        self.settings = settings or ProtocolSettings()
        self.exposed: list[ExposedCommand] = discover_exposed(typer_app)

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

        if mode is Mode.HYBRID and self._has_subcommand(argv):
            self._dispatch_cli(argv)
            return

        report = self._capability_check()
        if report.ok:
            report = CapabilityReport(False, "textual surface not implemented yet")

        if self.settings.fallback is Fallback.ERROR:
            raise ProtocolUnavailable(report.reason or "tui unavailable")

        self._dispatch_fallback(console=console, stdin=stdin)

    @staticmethod
    def _has_subcommand(argv: list[str]) -> bool:
        if not argv:
            return False
        return not argv[0].startswith("-")

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
