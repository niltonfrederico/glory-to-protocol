from __future__ import annotations

from typing import Annotated

import typer
from typer.testing import CliRunner

from glory_to_protocol.typer import make_app


def _bureau_app() -> typer.Typer:
    app = make_app(name="bureau", help="Bureau ops CLI for testing.")

    @app.callback()
    def _root(
        loud: Annotated[bool, typer.Option("--loud", help="Modo verboso.")] = False,
    ) -> None:
        return

    @app.command("ping")
    def ping_cmd(
        target: Annotated[str, typer.Argument(help="Alvo do ping.")],
        count: Annotated[int, typer.Option("--count", "-n", help="Número de pacotes.")] = 4,
        debug: Annotated[bool, typer.Option("--debug", help="Logs detalhados.")] = False,
    ) -> None:
        typer.echo(f"pong {target} x {count}")

    @app.command("noop")
    def noop_cmd() -> None:
        """Comando sem opções nem argumentos."""
        typer.echo("noop")

    return app


def test_should_render_logo_and_form_borders_when_group_help_runs() -> None:
    result = CliRunner().invoke(_bureau_app(), ["--help"])
    assert result.exit_code == 0, result.output
    assert "NIRVYTEKH" in result.output
    assert "╔" in result.output and "╝" in result.output
    assert "help · bureau" in result.output


def test_should_list_commands_with_drill_down_hint_when_group_help_runs() -> None:
    result = CliRunner().invoke(_bureau_app(), ["--help"])
    assert "Comandos:" in result.output
    assert "ping" in result.output
    assert "noop" in result.output
    assert "→ bureau ping --help" in result.output
    assert "→ bureau noop --help" in result.output


def test_should_show_flags_and_defaults_when_command_help_runs() -> None:
    result = CliRunner().invoke(_bureau_app(), ["ping", "--help"])
    assert result.exit_code == 0, result.output
    assert "help · bureau ping" in result.output
    assert "--count, -n" in result.output
    assert "Número de pacotes." in result.output
    assert "[default: 4]" in result.output
    assert "--debug" in result.output


def test_should_render_arguments_section_when_command_has_arguments() -> None:
    result = CliRunner().invoke(_bureau_app(), ["ping", "--help"])
    assert "Argumentos:" in result.output
    assert "TARGET" in result.output


def test_should_omit_options_section_when_command_has_no_options() -> None:
    result = CliRunner().invoke(_bureau_app(), ["noop", "--help"])
    assert result.exit_code == 0, result.output
    assert "Opções:" not in result.output
    assert "Comando sem opções nem argumentos." in result.output
