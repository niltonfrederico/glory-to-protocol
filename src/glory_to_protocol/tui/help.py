from __future__ import annotations

import textwrap

import click
from rich.console import Console
from rich.text import Text
from typer.core import TyperCommand
from typer.core import TyperGroup

from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.logo import LOGO_SMALL
from glory_to_protocol.tui.width import cell_len

_BODY_WIDTH = 72  # leaves margin inside the FORM_WIDTH=80 frame
_NBSP = " "  # Form._wrap_cells splits on " "; NBSP survives as visible indent.
_INDENT_2 = _NBSP * 2
_INDENT_4 = _NBSP * 4


def _flag_label(opt: click.Option) -> str:
    longs = [o for o in opt.opts if o.startswith("--")]
    shorts = [o for o in opt.opts if not o.startswith("--")]
    parts: list[str] = []
    if longs:
        parts.append(longs[0])
    if shorts:
        parts.append(shorts[0])
    label = ", ".join(parts) or (opt.opts[0] if opt.opts else opt.name or "?")
    if opt.is_flag:
        return label
    type_name = getattr(opt.type, "name", "TEXT")
    return f"{label} {type_name.upper()}"


def _argument_label(arg: click.Argument) -> str:
    name = (arg.name or "ARG").upper()
    if arg.nargs == -1:
        name = f"{name}..."
    return name if arg.required else f"[{name}]"


def _default_hint(opt: click.Option) -> str:
    if not opt.show_default and opt.default in (None, False, (), [], ""):
        return ""
    if opt.default in (None, False):
        return ""
    return f"[default: {opt.default}]"


def _first_line(text: str | None) -> str:
    if not text:
        return ""
    stripped = text.strip()
    return stripped.splitlines()[0].strip() if stripped else ""


def _wrap_indented(text: str, *, indent: str = _INDENT_4) -> list[str]:
    if not text:
        return []
    wrapped = textwrap.wrap(
        text,
        width=_BODY_WIDTH - len(indent),
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [f"{indent}{line}" for line in wrapped] or [indent]


def _usage_line(ctx: click.Context, command: click.Command, *, is_group: bool) -> str:
    pieces: list[str] = [ctx.command_path]
    options = [p for p in command.params if isinstance(p, click.Option) and not p.hidden]
    if options:
        pieces.append("[OPTIONS]")
    for arg in command.params:
        if isinstance(arg, click.Argument):
            pieces.append(_argument_label(arg))
    if is_group:
        pieces.append("COMMAND [ARGS]...")
    return " ".join(pieces)


def render_norman_help(ctx: click.Context) -> None:
    """Render --help output in the bureau's TUI aesthetic."""
    command = ctx.command
    is_group = isinstance(command, click.Group)
    console = Console(highlight=False, soft_wrap=False)

    title = f"help · {ctx.command_path}"
    with Form(title=title, console=console) as form:
        help_text = (command.help or "").strip()
        if help_text:
            for raw_line in help_text.splitlines():
                for line in _wrap_indented(raw_line.strip(), indent=""):
                    form.line(line)
            form.divider()

        form.line("Uso:", style=theme.HEADER)
        for line in _wrap_indented(_usage_line(ctx, command, is_group=is_group)):
            form.line(line)

        arguments = [p for p in command.params if isinstance(p, click.Argument)]
        if arguments:
            form.divider()
            form.line("Argumentos:", style=theme.HEADER)
            for arg in arguments:
                form.line(f"{_INDENT_2}{_argument_label(arg)}", style=theme.CYRILLIC_ACCENT)

        options = [p for p in command.params if isinstance(p, click.Option) and not p.hidden]
        if options:
            form.divider()
            form.line("Opções:", style=theme.HEADER)
            for index, opt in enumerate(options):
                if index > 0:
                    form.line("")
                form.line(f"{_INDENT_2}{_flag_label(opt)}", style=theme.CYRILLIC_ACCENT)
                desc = (opt.help or "").strip()
                if desc:
                    for line in _wrap_indented(desc):
                        form.line(line)
                hint = _default_hint(opt)
                if hint:
                    form.line(f"{_INDENT_4}{hint}", style=theme.MUTED)

        if is_group:
            subcommands = sorted(command.list_commands(ctx))
            if subcommands:
                form.divider()
                form.line("Comandos:", style=theme.HEADER)
                for index, name in enumerate(subcommands):
                    sub = command.get_command(ctx, name)
                    if sub is None:
                        continue
                    if index > 0:
                        form.line("")
                    form.line(f"{_INDENT_2}{name}", style=theme.CYRILLIC_ACCENT)
                    short = _first_line(sub.short_help or sub.help)
                    if short:
                        for line in _wrap_indented(short):
                            form.line(line)
                    form.line(
                        f"{_INDENT_4}→ {ctx.command_path} {name} --help",
                        style=theme.MUTED,
                    )

    _print_right_aligned_stamp(console)


def _print_right_aligned_stamp(console: Console) -> None:
    """Print LOGO_SMALL right-aligned within FORM_WIDTH, after the form closes."""
    for raw_line in LOGO_SMALL.splitlines():
        pad = max(theme.FORM_WIDTH - cell_len(raw_line), 0)
        text = Text(" " * pad)
        text.append(raw_line, style=theme.HEADER)
        console.print(text)


class NormanTyperGroup(TyperGroup):
    """TyperGroup that renders --help via the bureau TUI."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        render_norman_help(ctx)


class NormanTyperCommand(TyperCommand):
    """TyperCommand variant that renders --help via the bureau TUI."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        render_norman_help(ctx)
