from enum import StrEnum
from pathlib import Path
from typing import Annotated
from typing import Any

import typer
from textual.app import App
from textual.app import ComposeResult
from textual.widgets import Checkbox
from textual.widgets import Input
from textual.widgets import Select
from textual.widgets import Static

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.screens.form import FormScreen


class Severity(StrEnum):
    LOW = "low"
    HIGH = "high"


def _build_protocol() -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    @typer_app.command()
    @expose(section="data", icon="*")
    def ingest(
        path: str,
        retries: Annotated[int, typer.Option(help="How many retries to attempt.")] = 3,
        ratio: float = 1.0,
        dry_run: bool = False,
        output: Annotated[Path, typer.Option()] = Path("/tmp/out"),
        severity: Annotated[Severity, typer.Option()] = Severity.LOW,
    ) -> None:
        """Pull data into the warehouse."""
        typer.echo(f"ingest:{path}")

    return Protocol(typer_app=typer_app, settings=ProtocolSettings())


def _click_command(protocol: Protocol, typer_name: str) -> Any:
    import click

    cli = protocol.cli
    assert isinstance(cli, click.Group)
    return cli.commands[typer_name]


def _exposed(protocol: Protocol, typer_name: str) -> ExposedCommand:
    return next(e for e in protocol.exposed if e.typer_name == typer_name)


class _FormHost(App):
    def __init__(self, protocol: Protocol, form: FormScreen) -> None:
        self._theme = protocol.settings.layout.bureau
        self._form = form
        self.submitted: list[FormScreen.Submitted] = []
        self.cancelled: list[FormScreen.Cancelled] = []
        super().__init__()

    def get_css_variables(self) -> dict[str, str]:
        base = super().get_css_variables()
        base.update(
            {
                "accent": self._theme.accent,
                "gold": self._theme.gold,
                "bg": self._theme.bg,
                "border": self._theme.border,
                "muted": self._theme.muted,
                "text-color": self._theme.text_color,
                "bg-tint": self._theme.bg,
            }
        )
        return base

    def compose(self) -> ComposeResult:
        yield self._form

    def on_form_screen_submitted(self, message: FormScreen.Submitted) -> None:
        self.submitted.append(message)

    def on_form_screen_cancelled(self, message: FormScreen.Cancelled) -> None:
        self.cancelled.append(message)


async def test_should_render_input_widget_per_supported_primitive():
    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    app = _FormHost(protocol, form)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(form.query_one("#field-path"), Input)
        assert form.query_one("#field-retries", Input).type == "integer"
        assert form.query_one("#field-ratio", Input).type == "number"
        assert isinstance(form.query_one("#field-dry_run"), Checkbox)
        assert isinstance(form.query_one("#field-severity"), Select)


async def test_should_render_unsupported_label_when_annotation_unknown():
    # Synthesize a FormField with a type fields_from_typer would never produce
    # (a defensive guard for future schema extensions).
    from glory_to_protocol.tui._schema import FormField

    class _Custom:
        pass

    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    form._fields = [  # type: ignore[attr-defined]
        FormField(
            name="weird",
            annotation=_Custom,
            default=Ellipsis,
            help="",
            choices=None,
            multiple=False,
            hidden=False,
        )
    ]
    app = _FormHost(protocol, form)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        unsupported = form.query(Static).filter(".unsupported")
        assert len(unsupported) >= 1
        # Submitting with an unsupported field should produce empty kwargs.
        await pilot.click("#submit")
        await pilot.pause()
    assert app.submitted
    assert app.submitted[0].kwargs == {}


async def test_should_omit_select_value_when_default_missing_and_left_blank():
    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    app = _FormHost(protocol, form)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        # Clear the Select to BLANK then submit.
        form.query_one("#field-severity", Select).clear()
        await pilot.click("#submit")
        await pilot.pause()
    assert app.submitted
    kwargs = app.submitted[0].kwargs
    # severity had a default ("low"), and we cleared it → falls back to default.
    assert kwargs["severity"] == Severity.LOW


async def test_should_submit_with_coerced_values_when_approve_pressed():
    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    app = _FormHost(protocol, form)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        form.query_one("#field-path", Input).value = "/var/data"
        form.query_one("#field-retries", Input).value = "7"
        form.query_one("#field-ratio", Input).value = "2.5"
        form.query_one("#field-dry_run", Checkbox).value = True
        await pilot.click("#submit")
        await pilot.pause()

    assert app.submitted, "Expected Submitted message"
    kwargs = app.submitted[0].kwargs
    assert kwargs["path"] == "/var/data"
    assert kwargs["retries"] == 7
    assert kwargs["ratio"] == 2.5
    assert kwargs["dry_run"] is True
    assert kwargs["output"] == Path("/tmp/out")


async def test_should_emit_cancelled_when_cancel_button_pressed():
    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    app = _FormHost(protocol, form)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.click("#cancel")
        await pilot.pause()

    assert app.cancelled, "Expected Cancelled message"


async def test_should_emit_cancelled_when_escape_action_called():
    protocol = _build_protocol()
    command = _exposed(protocol, "ingest")
    form = FormScreen(command, _click_command(protocol, command.typer_name))
    app = _FormHost(protocol, form)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await form.run_action("cancel")
        await pilot.pause()

    assert app.cancelled, "Expected Cancelled message"
