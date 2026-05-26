from io import StringIO

import pytest
import typer
from click.testing import CliRunner
from rich.console import Console

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.protocol import ProtocolUnavailable
from glory_to_protocol.protocol import _terminal_size
from glory_to_protocol.protocol import _textual_importable
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import Fallback
from glory_to_protocol.settings import Mode
from glory_to_protocol.settings import ProtocolSettings


def _force_no_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)


def _force_full_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    monkeypatch.setattr(
        "glory_to_protocol.protocol._terminal_size",
        lambda: (100, 30),
    )
    monkeypatch.setattr(
        "glory_to_protocol.protocol._textual_importable",
        lambda: True,
    )


def _build_app() -> typer.Typer:
    app = typer.Typer()

    @app.callback()
    def _root():
        pass

    @app.command()
    @expose(section="data")
    def ingest(path: str):
        typer.echo(f"ingested:{path}")

    return app


def test_should_expose_typer_app_when_protocol_constructed():
    app = _build_app()
    protocol = Protocol(typer_app=app)
    assert protocol.typer_app is app


def test_should_load_exposed_commands_on_construction():
    app = _build_app()
    protocol = Protocol(typer_app=app)
    assert len(protocol.exposed) == 1
    assert protocol.exposed[0].section == "data"


def test_should_use_provided_settings_when_passed():
    app = _build_app()
    settings = ProtocolSettings(mode=Mode.CLI)
    protocol = Protocol(typer_app=app, settings=settings)
    assert protocol.settings.mode is Mode.CLI


def test_should_dispatch_typer_when_mode_cli():
    app = _build_app()
    protocol = Protocol(typer_app=app, settings=ProtocolSettings(mode=Mode.CLI))
    runner = CliRunner()
    result = runner.invoke(protocol.cli, ["ingest", "/tmp/x"])
    assert result.exit_code == 0
    assert "ingested:/tmp/x" in result.stdout


def test_should_run_cli_dispatch_when_mode_cli_and_argv_provided():
    app = _build_app()
    protocol = Protocol(typer_app=app, settings=ProtocolSettings(mode=Mode.CLI))
    # run() with explicit argv invokes _dispatch_cli; click.main raises SystemExit(0) on success.
    with pytest.raises(SystemExit) as exc_info:
        protocol.run(argv=["ingest", "/tmp/y"])
    assert exc_info.value.code == 0


def test_should_degrade_to_rich_when_mode_tui_and_no_tty(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    console = Console(file=StringIO(), record=True, width=100, force_terminal=False)
    protocol.run(argv=[], console=console, stdin=StringIO("1\n/tmp/x\n"))
    output = console.export_text()
    assert "ingest" in output.lower()


def test_should_raise_protocol_unavailable_when_fallback_is_error(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.ERROR),
    )
    _force_no_tty(monkeypatch)
    with pytest.raises(ProtocolUnavailable):
        protocol.run(argv=[])


def test_should_return_zero_size_when_no_terminal(monkeypatch):
    import os

    def raise_oserror(*_args, **_kwargs):
        raise OSError("no tty")

    monkeypatch.setattr(os, "get_terminal_size", raise_oserror)
    assert _terminal_size() == (0, 0)


def test_should_return_bool_from_textual_importable():
    import importlib.util

    expected = importlib.util.find_spec("textual") is not None
    assert _textual_importable() is expected


def test_should_report_capability_ok_when_tty_and_textual_present(monkeypatch):
    app = _build_app()
    protocol = Protocol(typer_app=app)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    monkeypatch.setattr(
        "glory_to_protocol.protocol._terminal_size",
        lambda: (100, 30),
    )
    monkeypatch.setattr(
        "glory_to_protocol.protocol._textual_importable",
        lambda: True,
    )
    report = protocol._capability_check()
    assert report.ok is True
    assert report.reason is None


def test_should_report_not_ok_when_stdout_is_not_tty(monkeypatch):
    app = _build_app()
    protocol = Protocol(typer_app=app)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    report = protocol._capability_check()
    assert report.ok is False
    assert "tty" in (report.reason or "").lower()


def test_should_report_not_ok_when_textual_missing(monkeypatch):
    app = _build_app()
    protocol = Protocol(typer_app=app)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    monkeypatch.setattr(
        "glory_to_protocol.protocol._terminal_size",
        lambda: (100, 30),
    )
    monkeypatch.setattr(
        "glory_to_protocol.protocol._textual_importable",
        lambda: False,
    )
    report = protocol._capability_check()
    assert report.ok is False
    assert "textual" in (report.reason or "").lower()


def test_should_report_not_ok_when_terminal_too_small(monkeypatch):
    app = _build_app()
    protocol = Protocol(typer_app=app)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    monkeypatch.setattr(
        "glory_to_protocol.protocol._terminal_size",
        lambda: (40, 12),
    )
    monkeypatch.setattr(
        "glory_to_protocol.protocol._textual_importable",
        lambda: True,
    )
    report = protocol._capability_check()
    assert report.ok is False
    reason = report.reason or ""
    assert "80" in reason and "24" in reason


def test_should_degrade_to_rich_when_textual_capability_ok_but_not_implemented(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.RICH),
    )
    _force_full_tty(monkeypatch)
    console = Console(file=StringIO(), record=True, width=100, force_terminal=False)
    protocol.run(argv=[], console=console, stdin=StringIO("1\n/tmp/x\n"))
    output = console.export_text()
    assert "ingest" in output.lower()


def test_should_raise_protocol_unavailable_when_textual_ok_but_fallback_is_error(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.ERROR),
    )
    _force_full_tty(monkeypatch)
    with pytest.raises(ProtocolUnavailable, match="textual surface"):
        protocol.run(argv=[])


def test_should_use_degraded_palette_when_hybrid_without_subcommand(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    console = Console(file=StringIO(), record=True, width=100, force_terminal=False)
    protocol.run(argv=[], console=console, stdin=StringIO("1\n/tmp/x\n"))
    output = console.export_text()
    assert "ingest" in output.lower()


def test_should_dispatch_typer_when_mode_hybrid_with_subcommand(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(protocol.cli, ["ingest", "/tmp/x"])
    assert result.exit_code == 0
    assert "ingested:/tmp/x" in result.stdout


def test_should_raise_when_fallback_called_with_empty_exposed(monkeypatch):
    app = typer.Typer()

    @app.command()
    def naked():
        typer.echo("naked")

    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    with pytest.raises(ProtocolUnavailable, match="no exposed commands"):
        protocol.run(argv=[])


def test_should_dispatch_cli_when_mode_hybrid_with_subcommand_via_run(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    with pytest.raises(SystemExit) as exc_info:
        protocol.run(argv=["ingest", "/tmp/z"])
    assert exc_info.value.code == 0


def test_should_dispatch_cli_when_mode_cli_via_run(monkeypatch):
    app = _build_app()
    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.CLI, fallback=Fallback.RICH),
    )
    with pytest.raises(SystemExit) as exc_info:
        protocol.run(argv=["ingest", "/tmp/z"])
    assert exc_info.value.code == 0


def test_should_raise_when_cli_not_a_group(monkeypatch):
    app = typer.Typer()

    @app.command()
    @expose(section="data")
    def single(path: str):
        typer.echo(f"single:{path}")

    protocol = Protocol(
        typer_app=app,
        settings=ProtocolSettings(mode=Mode.TUI, fallback=Fallback.RICH),
    )
    _force_no_tty(monkeypatch)
    # Single-command Typer app without @app.callback() resolves to click.BaseCommand, not Group.
    console = Console(file=StringIO(), record=True, width=100, force_terminal=False)
    with pytest.raises(ProtocolUnavailable, match="click.Group"):
        protocol.run(argv=[], console=console, stdin=StringIO("1\n/tmp/x\n"))
