from __future__ import annotations

import sys
from typing import Any
from typing import TextIO

from rich.console import Console
from rich.prompt import Confirm
from rich.prompt import IntPrompt
from rich.prompt import Prompt

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.settings import get_settings
from glory_to_protocol.tui._schema import FormField
from glory_to_protocol.tui.header import render_header


def render_header_oneshot(
    *,
    console: Console | None = None,
    settings: ProtocolSettings | None = None,
) -> None:
    """Print the bureau header once. Reuses the existing Rich renderable."""
    _settings = settings or get_settings()
    _ = _settings  # currently unused; future overrides may consume it
    active_console = console or Console(highlight=False, soft_wrap=False)
    active_console.print(render_header())


def prompt_form(
    fields: list[FormField],
    *,
    console: Console | None = None,
    stdin: TextIO | None = None,
) -> dict[str, Any]:
    """Walk a list of FormField and prompt the operator via Rich prompts."""
    active_console = console or Console(highlight=False, soft_wrap=False)
    stream: TextIO = stdin or sys.stdin
    values: dict[str, Any] = {}
    for field in fields:
        values[field.name] = _ask_one(field, console=active_console, stream=stream)
    return values


def _ask_one(field: FormField, *, console: Console, stream: TextIO) -> Any:
    label = field.name + (f" ({field.help})" if field.help else "")
    default = field.default
    if field.annotation is bool:
        return Confirm.ask(
            label,
            console=console,
            stream=stream,
            default=bool(default) if default is not Ellipsis else False,
        )
    if field.choices is not None:
        return Prompt.ask(
            label,
            console=console,
            stream=stream,
            choices=list(field.choices),
            default=None if default is Ellipsis else default,
        )
    if field.annotation is int:
        return IntPrompt.ask(
            label,
            console=console,
            stream=stream,
            default=None if default is Ellipsis else int(default),
        )
    return Prompt.ask(
        label,
        console=console,
        stream=stream,
        default=None if default is Ellipsis else str(default),
    )


def degraded_palette(
    commands: list[ExposedCommand],
    *,
    console: Console | None = None,
    stdin: TextIO | None = None,
) -> ExposedCommand:
    """Numbered palette used when stdio is not a tty but mode is tui/hybrid.

    Prints commands 1..N with their labels, prompts for an index, and returns
    the chosen ExposedCommand. Re-prompts on out-of-range input.
    """
    if not commands:
        raise ValueError("palette is empty")
    active_console = console or Console(highlight=False, soft_wrap=False)
    stream: TextIO = stdin or sys.stdin
    for index, entry in enumerate(commands, start=1):
        active_console.print(f"  {index}. {entry.label}")
    while True:
        choice = IntPrompt.ask(
            "select",
            console=active_console,
            stream=stream,
            default=1,
        )
        if 1 <= choice <= len(commands):
            return commands[choice - 1]
        active_console.print(f"out of range (1..{len(commands)})")
