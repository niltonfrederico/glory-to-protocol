import dataclasses

import pytest
import typer

from glory_to_protocol.registry import EXPOSE_ATTR
from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.registry import expose


def test_should_attach_exposed_command_when_decorator_applied():
    @expose(section="data", shortcut="ctrl+d")
    def cmd(path: str): ...

    info = getattr(cmd, EXPOSE_ATTR)
    assert isinstance(info, ExposedCommand)
    assert info.section == "data"
    assert info.shortcut == "ctrl+d"


def test_should_default_label_to_callback_name_when_label_not_provided():
    @expose()
    def ingest_file(): ...

    info = getattr(ingest_file, EXPOSE_ATTR)
    assert info.label == "ingest file"


def test_should_extract_description_from_docstring_when_present():
    @expose()
    def cmd():
        """Ingerir arquivo no ledger."""

    info = getattr(cmd, EXPOSE_ATTR)
    assert info.description == "Ingerir arquivo no ledger."


def test_should_hide_when_hidden_true():
    @expose(hidden=True)
    def cmd(): ...

    info = getattr(cmd, EXPOSE_ATTR)
    assert info.hidden is True


def test_should_preserve_callable_when_decorator_applied():
    @expose()
    def cmd(x: int) -> int:
        return x * 2

    assert cmd(3) == 6


def test_should_be_frozen_dataclass_with_slots():
    info = ExposedCommand(
        callback=lambda: None,
        typer_name="x",
        label="x",
        section=None,
        shortcut=None,
        description="",
        form=None,
        icon=None,
        hidden=False,
    )
    assert dataclasses.is_dataclass(info)
    assert info.__dataclass_params__.frozen is True
    assert "__slots__" in type(info).__dict__


def test_should_keep_label_when_explicit_label_passed():
    @expose(label="Custom Label")
    def cmd(): ...

    assert getattr(cmd, EXPOSE_ATTR).label == "Custom Label"


def test_should_set_typer_name_from_callback_name_in_kebab():
    @expose()
    def ingest_file_batch(): ...

    info = getattr(ingest_file_batch, EXPOSE_ATTR)
    assert info.typer_name == "ingest-file-batch"


def test_should_empty_description_when_no_docstring():
    @expose()
    def cmd(): ...

    assert getattr(cmd, EXPOSE_ATTR).description == ""


def test_should_discover_exposed_commands_when_walking_typer_app():
    from glory_to_protocol.registry import discover_exposed

    app = typer.Typer()

    @app.command()
    @expose(section="data")
    def ingest(path: str): ...

    @app.command()
    def not_exposed(): ...

    exposed = discover_exposed(app)
    assert len(exposed) == 1
    assert exposed[0].section == "data"
    assert exposed[0].callback is ingest


def test_should_raise_when_two_exposed_commands_share_shortcut():
    from glory_to_protocol.registry import discover_exposed

    app = typer.Typer()

    @app.command()
    @expose(shortcut="ctrl+d")
    def a(): ...

    @app.command()
    @expose(shortcut="ctrl+d")
    def b(): ...

    with pytest.raises(ValueError, match="ctrl\\+d"):
        discover_exposed(app)


def test_should_skip_hidden_commands_in_palette_view():
    from glory_to_protocol.registry import discover_exposed
    from glory_to_protocol.registry import palette_entries

    app = typer.Typer()

    @app.command()
    @expose()
    def visible(): ...

    @app.command()
    @expose(hidden=True)
    def secret(): ...

    discovered = discover_exposed(app)
    palette = palette_entries(discovered)
    assert {getattr(e.callback, "__name__", None) for e in discovered} == {"visible", "secret"}
    assert {getattr(e.callback, "__name__", None) for e in palette} == {"visible"}


def test_should_return_empty_list_when_no_exposed_commands():
    from glory_to_protocol.registry import discover_exposed

    app = typer.Typer()

    @app.command()
    def bare(): ...

    assert discover_exposed(app) == []
