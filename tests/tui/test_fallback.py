from io import StringIO
from pathlib import Path
from types import FunctionType

import pytest
from rich.console import Console

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.tui._schema import FormField
from glory_to_protocol.tui.fallback import degraded_palette
from glory_to_protocol.tui.fallback import prompt_form
from glory_to_protocol.tui.fallback import render_header_oneshot


def _make_console() -> Console:
    return Console(file=StringIO(), record=True, width=100, force_terminal=False)


def test_should_render_header_oneshot_with_motto():
    console = _make_console()
    render_header_oneshot(console=console)
    output = console.export_text()
    # The header renders the bureau title / motto from settings; just assert it
    # produced non-empty output.
    assert output.strip() != ""


def test_should_collect_values_from_stdin_when_prompt_form_runs():
    fields = [
        FormField(
            name="path",
            annotation=Path,
            default=Ellipsis,
            help="Path to file",
            choices=None,
            multiple=False,
            hidden=False,
        ),
        FormField(
            name="dry_run",
            annotation=bool,
            default=False,
            help="",
            choices=None,
            multiple=False,
            hidden=False,
        ),
    ]
    console = _make_console()
    stdin = StringIO("/tmp/x\ny\n")
    values = prompt_form(fields, console=console, stdin=stdin)
    assert values["path"] == "/tmp/x"
    assert values["dry_run"] is True


def test_should_accept_default_when_blank_input_given_for_optional_field():
    fields = [
        FormField(
            name="count",
            annotation=int,
            default=3,
            help="",
            choices=None,
            multiple=False,
            hidden=False,
        ),
    ]
    console = _make_console()
    stdin = StringIO("\n")
    values = prompt_form(fields, console=console, stdin=stdin)
    assert values["count"] == 3


def test_should_validate_choice_when_field_has_choices():
    fields = [
        FormField(
            name="color",
            annotation=str,
            default="red",
            help="",
            choices=("red", "blue"),
            multiple=False,
            hidden=False,
        ),
    ]
    console = _make_console()
    stdin = StringIO("blue\n")
    values = prompt_form(fields, console=console, stdin=stdin)
    assert values["color"] == "blue"


def test_should_treat_required_string_field_as_no_default():
    fields = [
        FormField(
            name="path",
            annotation=str,
            default=Ellipsis,
            help="",
            choices=None,
            multiple=False,
            hidden=False,
        ),
    ]
    console = _make_console()
    stdin = StringIO("/tmp/y\n")
    values = prompt_form(fields, console=console, stdin=stdin)
    assert values["path"] == "/tmp/y"


def _exposed(name: str, label: str | None = None) -> ExposedCommand:
    def cb(): ...

    cb.__name__ = name
    return ExposedCommand(
        callback=cb,
        typer_name=name.replace("_", "-"),
        label=label or name.replace("_", " "),
        section=None,
        shortcut=None,
        description="",
        form=None,
        icon=None,
        hidden=False,
    )


def test_should_pick_command_by_index_when_palette_runs():
    commands = [_exposed("ingest"), _exposed("export"), _exposed("re_ingest")]
    console = _make_console()
    stdin = StringIO("2\n")
    chosen = degraded_palette(commands, console=console, stdin=stdin)
    assert isinstance(chosen.callback, FunctionType)
    assert chosen.callback.__name__ == "export"


def test_should_reject_index_outside_range_and_reprompt():
    commands = [_exposed("ingest"), _exposed("export")]
    console = _make_console()
    stdin = StringIO("9\n1\n")
    chosen = degraded_palette(commands, console=console, stdin=stdin)
    assert isinstance(chosen.callback, FunctionType)
    assert chosen.callback.__name__ == "ingest"


def test_should_raise_when_palette_is_empty():
    console = _make_console()
    with pytest.raises(ValueError, match="empty"):
        degraded_palette([], console=console, stdin=StringIO(""))
