from __future__ import annotations

from typing import Annotated

import click
import typer
from typer.testing import CliRunner

from glory_to_protocol.tui.help import _argument_label
from glory_to_protocol.tui.help import _default_hint
from glory_to_protocol.tui.help import _first_line
from glory_to_protocol.tui.help import _wrap_indented
from glory_to_protocol.typer import make_app


def test_should_render_varargs_label_when_argument_nargs_is_minus_one() -> None:
    arg = click.Argument(["targets"], nargs=-1)
    assert _argument_label(arg) == "[TARGETS...]"


def test_should_return_empty_string_when_default_is_none_and_show_default() -> None:
    opt = click.Option(["--name"], default=None, show_default=True)
    assert _default_hint(opt) == ""


def test_should_return_empty_string_when_default_is_false_and_show_default() -> None:
    opt = click.Option(["--flag/--no-flag"], default=False, show_default=True)
    assert _default_hint(opt) == ""


def test_should_return_empty_string_when_first_line_called_with_none() -> None:
    assert _first_line(None) == ""


def test_should_return_empty_list_when_wrap_indented_called_with_empty() -> None:
    assert _wrap_indented("") == []


def test_should_show_varargs_in_usage_when_command_has_varargs() -> None:
    app = make_app(name="bureau")

    @app.command("multi")
    def multi_cmd(
        items: Annotated[list[str], typer.Argument(help="N items.")],
    ) -> None:
        typer.echo(" ".join(items))

    result = CliRunner().invoke(app, ["multi", "--help"])
    assert result.exit_code == 0, result.output
    assert "ITEMS..." in result.output
