from enum import StrEnum
from pathlib import Path

import click
import typer

from glory_to_protocol.tui._schema import FormField
from glory_to_protocol.tui._schema import fields_from_typer


class Color(StrEnum):
    RED = "red"
    BLUE = "blue"


def _command_from(callback) -> click.Command:
    app = typer.Typer()
    app.command()(callback)
    cmd = typer.main.get_command(app)
    if isinstance(cmd, click.Group):
        name = next(iter(cmd.commands))
        return cmd.commands[name]
    return cmd  # type: ignore[return-value]


def test_should_extract_required_field_when_param_has_no_default():
    def cmd(path: Path):
        pass

    fields = fields_from_typer(_command_from(cmd))
    [path] = [f for f in fields if f.name == "path"]
    assert path.default is Ellipsis
    assert path.annotation is Path


def test_should_extract_default_when_param_has_one():
    def cmd(dry_run: bool = False):
        pass

    [field] = fields_from_typer(_command_from(cmd))
    assert field.default is False
    assert field.annotation is bool


def test_should_extract_choices_when_param_annotation_is_enum():
    def cmd(color: Color = Color.RED):
        pass

    [field] = fields_from_typer(_command_from(cmd))
    assert field.choices == ("red", "blue")


def test_should_skip_hidden_params():
    def cmd(visible: int = 1, secret: int = typer.Option(0, hidden=True)):  # noqa: B008
        pass

    fields = fields_from_typer(_command_from(cmd))
    names = {f.name for f in fields}
    assert names == {"visible"}


def test_should_extract_help_text_when_provided():
    def cmd(path: Path = typer.Argument(..., help="Path to file")):  # noqa: B008
        pass

    [field] = fields_from_typer(_command_from(cmd))
    assert field.help == "Path to file"


def test_should_flag_multiple_when_param_takes_list():
    def cmd(tags: list[str] = typer.Option([])):  # noqa: B008
        pass

    [field] = fields_from_typer(_command_from(cmd))
    assert field.multiple is True


def test_should_extract_float_annotation_when_param_type_is_float():
    def cmd(threshold: float = 0.5):
        pass

    [field] = fields_from_typer(_command_from(cmd))
    assert field.annotation is float
    assert field.default == 0.5


def test_should_return_frozen_dataclass_with_slots():
    field = FormField(
        name="x",
        annotation=int,
        default=1,
        help="",
        choices=None,
        multiple=False,
        hidden=False,
    )
    import dataclasses

    assert dataclasses.is_dataclass(field)
    assert field.__dataclass_params__.frozen is True
    assert "__slots__" in type(field).__dict__
