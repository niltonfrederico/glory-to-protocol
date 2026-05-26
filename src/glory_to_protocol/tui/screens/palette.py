from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable
from textual.widgets import Input

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.registry import palette_entries
from glory_to_protocol.tui._branding import body_subtitle


class PaletteScreen(Vertical):
    """Lists exposed commands grouped by section.

    Despite the "Screen" suffix this is a `Vertical` container — it lives inside
    `ProtocolApp` body so `OfficialHeader` and `BindingsFooter` stay docked.
    Emits `Selected(ExposedCommand)` when the operator picks a row.
    """

    BINDINGS = [
        Binding("j", "cursor_down", "down", show=False),
        Binding("k", "cursor_up", "up", show=False),
        Binding("slash", "focus_filter", "filter", show=True),
    ]

    DEFAULT_CSS = """
    PaletteScreen {
        width: 100%;
        height: 1fr;
        background: $bg;
        align: center top;
        padding: 0;
    }
    PaletteScreen #filter {
        width: 60;
        max-width: 80%;
        height: 1;
        border: none;
        background: $bg;
        color: $text-color;
        padding: 0 1;
        margin: 0;
    }
    PaletteScreen DataTable {
        height: 1fr;
        border: heavy $accent;
        border-subtitle-color: $gold;
        background: $bg;
        margin-top: 0;
    }
    PaletteScreen DataTable > .datatable--header {
        background: $bg;
        color: $gold;
        text-style: bold;
    }
    PaletteScreen DataTable > .datatable--odd-row,
    PaletteScreen DataTable > .datatable--even-row {
        background: $bg;
    }
    """

    class Selected(Message):
        def __init__(self, command: ExposedCommand) -> None:
            self.command = command
            super().__init__()

    def __init__(self, exposed: list[ExposedCommand]) -> None:
        super().__init__()
        self._exposed = palette_entries(exposed)
        self._filter = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter… (press / to focus)", id="filter")
        yield DataTable(zebra_stripes=True, cursor_type="row", id="commands")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Icon", "Command", "Section", "Description")
        table.border_subtitle = body_subtitle()
        self._populate(table)
        table.focus()

    def _populate(self, table: DataTable) -> None:
        table.clear()
        needle = self._filter.lower()
        for entry in self._exposed:
            haystack = " ".join(
                [entry.label, entry.section or "", entry.description, entry.typer_name]
            ).lower()
            if needle and needle not in haystack:
                continue
            table.add_row(
                entry.icon or " ",
                entry.label,
                entry.section or "",
                entry.description,
                key=entry.typer_name,
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        self._filter = event.value
        self._populate(self.query_one(DataTable))

    def action_focus_filter(self) -> None:
        self.query_one(Input).focus()

    def action_cursor_down(self) -> None:
        self.query_one(DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(DataTable).action_cursor_up()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        chosen = next(
            (e for e in self._exposed if e.typer_name == event.row_key.value),
            None,
        )
        if chosen is None:
            return
        self.post_message(self.Selected(chosen))
