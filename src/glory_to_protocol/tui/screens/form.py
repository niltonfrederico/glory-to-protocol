from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Button
from textual.widgets import Checkbox
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import Static
from textual.widgets._input import InputType

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.tui._schema import FormField
from glory_to_protocol.tui._schema import fields_from_typer

_SUPPORTED_PRIMITIVES = {bool, str, int, float, Path}


def _input_type(annotation: type) -> InputType:
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    return "text"


def _field_id(name: str) -> str:
    return f"field-{name}"


def _initial_value(field: FormField) -> str:
    if field.default is Ellipsis:
        return ""
    return str(field.default)


def _coerce(raw: str, annotation: type) -> Any:
    if annotation is int:
        return int(raw)
    if annotation is float:
        return float(raw)
    if annotation is Path:
        return Path(raw)
    return raw


class FormScreen(Vertical):
    """Renders inputs derived from a Typer command's parameters.

    Emits `Submitted(callback, kwargs)` when the operator confirms the form,
    or `Cancelled` if they back out via `escape`.
    """

    BINDINGS = [
        Binding("escape", "cancel", "back", show=False),
    ]

    DEFAULT_CSS = """
    FormScreen {
        border: heavy $accent;
        background: $bg;
        padding: 1 2;
    }
    FormScreen .field-label {
        color: $gold;
        padding: 1 0 0 0;
    }
    FormScreen .field-help {
        color: $muted;
    }
    FormScreen .unsupported {
        color: $muted;
        padding: 1 0;
    }
    FormScreen Button {
        margin: 1 1 0 0;
    }
    """

    class Submitted(Message):
        def __init__(self, callback: Callable[..., Any], kwargs: dict[str, Any]) -> None:
            self.callback = callback
            self.kwargs = kwargs
            super().__init__()

    class Cancelled(Message):
        pass

    def __init__(self, command: ExposedCommand, click_command: Any) -> None:
        super().__init__()
        self._command = command
        self._fields = fields_from_typer(click_command)

    def compose(self) -> ComposeResult:
        yield Static(self._command.label, classes="field-label")
        with VerticalScroll(id="form-body"):
            for field in self._fields:
                yield Label(field.name, classes="field-label")
                if field.help:
                    yield Static(field.help, classes="field-help")
                yield self._field_widget(field)
        yield Vertical(
            Button("Approve", id="submit", variant="primary"),
            Button("Cancel", id="cancel", variant="default"),
        )

    def _field_widget(self, field: FormField) -> Any:
        widget_id = _field_id(field.name)
        if field.choices is not None:
            options = [(choice, choice) for choice in field.choices]
            initial = field.default if field.default is not Ellipsis else Select.NULL
            return Select(options, value=initial, id=widget_id)
        annotation = field.annotation
        if annotation is bool:
            return Checkbox(
                field.name,
                value=bool(field.default) if field.default is not Ellipsis else False,
                id=widget_id,
            )
        if annotation in _SUPPORTED_PRIMITIVES:
            return Input(
                value=_initial_value(field),
                placeholder=field.help or field.name,
                type=_input_type(annotation),
                id=widget_id,
            )
        return Static(f"(unsupported type: {annotation.__name__})", classes="unsupported")

    def _collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for field in self._fields:
            if field.annotation not in _SUPPORTED_PRIMITIVES and field.choices is None:
                continue
            widget = self.query_one(f"#{_field_id(field.name)}")
            if isinstance(widget, Checkbox):
                values[field.name] = widget.value
            elif isinstance(widget, Select):
                value = widget.value
                if value is Select.NULL:
                    if field.default is not Ellipsis:
                        values[field.name] = field.default
                else:
                    values[field.name] = value
            elif isinstance(widget, Input):
                values[field.name] = _coerce(widget.value, field.annotation)
        return values

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.post_message(self.Submitted(self._command.callback, self._collect()))
        elif event.button.id == "cancel":
            self.post_message(self.Cancelled())

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled())
