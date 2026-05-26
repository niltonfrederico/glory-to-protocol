from io import StringIO

import typer
from rich.console import Console

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import LayoutSettings
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.identity import BureauTheme
from glory_to_protocol.tui.providers import ExposedCommandProvider
from glory_to_protocol.tui.screens.form import FormScreen
from glory_to_protocol.tui.screens.help import HelpOverlay
from glory_to_protocol.tui.screens.palette import PaletteScreen
from glory_to_protocol.tui.screens.result import render_result_stamp


def _build_protocol(layout: LayoutSettings | None = None) -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    @typer_app.command()
    @expose(section="data")
    def ingest(path: str) -> None:
        """Pull data."""

    settings = ProtocolSettings(layout=layout) if layout else ProtocolSettings()
    return Protocol(typer_app=typer_app, settings=settings)


async def test_should_open_help_overlay_when_question_mark_pressed():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await app.run_action("open_help")
        await pilot.pause()
        overlay = app.query_one(HelpOverlay)
        from textual.widgets import Static

        body = " ".join(str(s.renderable) for s in overlay.query(Static))
        assert "ДИРЕКТИВА" in body
        assert "S chestyu, NIRVYTEKH" in body
        assert "quit" in body


async def test_should_dismiss_help_overlay_when_escape_pressed():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await app.run_action("open_help")
        await pilot.pause()
        assert len(app.query(HelpOverlay)) == 1
        await pilot.press("escape")
        await pilot.pause()
        assert len(app.query(HelpOverlay)) == 0


async def test_should_show_custom_directive_prefix_when_theme_overridden():
    layout = LayoutSettings(
        bureau=BureauTheme(directive_prefix="DIRECTIVE №", sign_off="With honor, PROTON")
    )
    protocol = _build_protocol(layout=layout)
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await app.run_action("open_help")
        await pilot.pause()
        overlay = app.query_one(HelpOverlay)
        from textual.widgets import Static

        body = " ".join(str(s.renderable) for s in overlay.query(Static))
        assert "DIRECTIVE №" in body
        assert "With honor, PROTON" in body


async def test_should_register_exposed_command_provider_on_app():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    assert ExposedCommandProvider in app.COMMANDS


async def test_should_yield_hits_when_provider_searches_matching_query():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        provider = ExposedCommandProvider(app.screen)
        hits = [hit async for hit in provider.search("ingest")]
        assert len(hits) >= 1
        assert all(hit.score > 0 for hit in hits)


async def test_should_open_form_when_provider_hit_invoked():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        provider = ExposedCommandProvider(app.screen)
        hits = [hit async for hit in provider.search("ingest")]
        assert hits
        hits[0].command()
        await pilot.pause()
        assert len(app.query(FormScreen)) == 1


async def test_should_swap_to_form_when_provider_activates_command():
    protocol = _build_protocol()
    app = ProtocolApp(protocol)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        command = protocol.exposed[0]
        app.activate_exposed_command(command)
        await pilot.pause()
        assert len(app.query(FormScreen)) == 1
        assert len(app.query(PaletteScreen)) == 0


def test_should_render_approved_stamp_when_outcome_approved():
    protocol = _build_protocol()
    command = protocol.exposed[0]
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=100, record=True)
    render_result_stamp(command, "approved", console=console)
    output = console.export_text()
    assert "ОДОБРЕНО" in output or "APPROVED" in output


def test_should_render_rejected_stamp_when_outcome_rejected():
    protocol = _build_protocol()
    command = protocol.exposed[0]
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=100, record=True)
    render_result_stamp(command, "rejected", console=console, detail="oops")
    output = console.export_text()
    assert "ОТКАЗАНО" in output or "REJECTED" in output
    assert "oops" in output


def test_should_dispatch_callback_and_render_stamp_when_textual_returns_payload(monkeypatch):
    protocol = _build_protocol()
    invocations: list[str] = []

    def fake_callback(path: str) -> None:
        invocations.append(path)

    stamps: list[str] = []

    def fake_render(command, outcome, **_) -> None:  # noqa: ANN001
        stamps.append(outcome)

    monkeypatch.setattr("glory_to_protocol.protocol.render_result_stamp", fake_render)

    # Replace the exposed command's callback identity so `_dispatch_textual`
    # can match it after the Textual app exits.
    target = protocol.exposed[0]
    object.__setattr__(target, "callback", fake_callback)

    monkeypatch.setattr("textual.app.App.run", lambda self: (fake_callback, {"path": "/srv"}))
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("glory_to_protocol.protocol._terminal_size", lambda: (100, 30))
    monkeypatch.setattr("glory_to_protocol.protocol._textual_importable", lambda: True)

    from glory_to_protocol.settings import Mode

    protocol.settings = ProtocolSettings(mode=Mode.TUI)
    protocol._dispatch_textual()

    assert invocations == ["/srv"]
    assert stamps == ["approved"]


def test_should_render_rejected_stamp_when_callback_raises(monkeypatch):
    protocol = _build_protocol()

    def boom(path: str) -> None:
        raise RuntimeError("nope")

    stamps: list[str] = []

    def fake_render(command, outcome, **_) -> None:  # noqa: ANN001
        stamps.append(outcome)

    monkeypatch.setattr("glory_to_protocol.protocol.render_result_stamp", fake_render)

    target = protocol.exposed[0]
    object.__setattr__(target, "callback", boom)

    monkeypatch.setattr("textual.app.App.run", lambda self: (boom, {"path": "/srv"}))

    protocol._dispatch_textual()
    assert stamps == ["rejected"]
