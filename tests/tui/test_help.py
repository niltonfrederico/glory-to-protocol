from __future__ import annotations

import typer
from typer.testing import CliRunner


def test_should_render_logo_and_form_borders_when_group_help_runs(
    bureau_app: typer.Typer, cli_runner: CliRunner
) -> None:
    result = cli_runner.invoke(bureau_app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "Protocol" in result.output
    assert "╔" in result.output and "╝" in result.output
    assert "help · bureau" in result.output


def test_should_list_commands_with_drill_down_hint_when_group_help_runs(
    bureau_app: typer.Typer, cli_runner: CliRunner
) -> None:
    result = cli_runner.invoke(bureau_app, ["--help"])
    assert "Comandos:" in result.output
    assert "ping" in result.output
    assert "noop" in result.output
    assert "→ bureau ping --help" in result.output
    assert "→ bureau noop --help" in result.output


def test_should_show_flags_and_defaults_when_command_help_runs(
    bureau_app: typer.Typer, cli_runner: CliRunner
) -> None:
    result = cli_runner.invoke(bureau_app, ["ping", "--help"])
    assert result.exit_code == 0, result.output
    assert "help · bureau ping" in result.output
    assert "--count, -n" in result.output
    assert "Número de pacotes." in result.output
    assert "[default: 4]" in result.output
    assert "--debug" in result.output


def test_should_render_arguments_section_when_command_has_arguments(
    bureau_app: typer.Typer, cli_runner: CliRunner
) -> None:
    result = cli_runner.invoke(bureau_app, ["ping", "--help"])
    assert "Argumentos:" in result.output
    assert "TARGET" in result.output


def test_should_omit_options_section_when_command_has_no_options(
    bureau_app: typer.Typer, cli_runner: CliRunner
) -> None:
    result = cli_runner.invoke(bureau_app, ["noop", "--help"])
    assert result.exit_code == 0, result.output
    assert "Opções:" not in result.output
    assert "Comando sem opções nem argumentos." in result.output
