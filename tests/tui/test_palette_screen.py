import typer
from textual.widgets import DataTable
from textual.widgets import Input

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.screens.palette import PaletteScreen


def _build_protocol() -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    @typer_app.command()
    @expose(section="data", icon="◈")
    def ingest(path: str) -> None:
        """Pull data into the warehouse."""
        typer.echo(f"ingest:{path}")

    @typer_app.command()
    @expose(section="reports", icon="⌛")
    def daily(when: str) -> None:
        """Compile daily report."""
        typer.echo(f"daily:{when}")

    return Protocol(typer_app=typer_app, settings=ProtocolSettings())


async def test_should_list_all_exposed_commands_when_no_filter():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        assert table.row_count == 2


async def test_should_filter_rows_when_filter_input_changes():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.query_one(PaletteScreen)
        filter_input = screen.query_one(Input)
        filter_input.value = "ingest"
        await pilot.pause()
        table = app.query_one(DataTable)
        assert table.row_count == 1


async def test_should_emit_selected_when_row_picked():
    protocol = _build_protocol()
    captured: list[PaletteScreen.Selected] = []

    class _CapturingApp(ProtocolApp):
        def on_palette_screen_selected(self, message: PaletteScreen.Selected) -> None:
            captured.append(message)

    app = _CapturingApp(protocol)
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("enter")
        await pilot.pause()

    assert captured, "Expected at least one Selected message"
    assert captured[0].command.typer_name == "ingest"


async def test_should_navigate_with_j_and_k_keys():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        table.focus()
        assert table.cursor_row == 0
        await pilot.press("j")
        await pilot.pause()
        assert table.cursor_row == 1
        await pilot.press("k")
        await pilot.pause()
        assert table.cursor_row == 0


async def test_should_focus_filter_when_slash_pressed():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("slash")
        await pilot.pause()
        filter_input = app.query_one(Input)
        assert filter_input.has_focus
