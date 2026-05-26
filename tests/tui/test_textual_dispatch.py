import typer
from textual.widgets import DataTable
from textual.widgets import Input

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.screens.form import FormScreen
from glory_to_protocol.tui.screens.palette import PaletteScreen


def _build_protocol() -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    @typer_app.command()
    @expose(section="data", icon="◈")
    def ingest(path: str) -> None:
        """Pull data."""

    return Protocol(typer_app=typer_app, settings=ProtocolSettings())


async def test_should_swap_palette_for_form_when_command_selected():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert len(app.query(PaletteScreen)) == 1
        assert len(app.query(FormScreen)) == 0

        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("enter")
        await pilot.pause()

        assert len(app.query(PaletteScreen)) == 0
        assert len(app.query(FormScreen)) == 1


async def test_should_restore_palette_when_form_cancelled():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("enter")
        await pilot.pause()
        form = app.query_one(FormScreen)
        await form.run_action("cancel")
        await pilot.pause()

        assert len(app.query(PaletteScreen)) == 1
        assert len(app.query(FormScreen)) == 0


async def test_should_exit_app_with_callback_payload_when_form_submitted():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("enter")
        await pilot.pause()
        form = app.query_one(FormScreen)
        form.query_one("#field-path", Input).value = "/srv/data"
        callback = form._command.callback  # type: ignore[attr-defined]
        form.post_message(FormScreen.Submitted(callback, {"path": "/srv/data"}))
        await pilot.pause()

    assert app.return_value is not None
    returned_callback, kwargs = app.return_value
    assert kwargs == {"path": "/srv/data"}
    assert callable(returned_callback)
