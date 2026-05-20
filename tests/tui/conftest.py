from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

import pytest
import typer
from rich.console import Console
from typer.testing import CliRunner

from glory_to_protocol.typer import make_app

SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "logs" / "tui-snapshots"


@pytest.fixture(autouse=True)
def _ensure_snapshot_dir() -> Iterator[None]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture()
def snapshot_console() -> Console:
    """A recording console with a fixed width matching the form."""
    return Console(
        record=True,
        width=80,
        force_terminal=False,
        soft_wrap=False,
        highlight=False,
        legacy_windows=False,
    )


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def bureau_app() -> typer.Typer:
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


def save_snapshot(name: str, content: str) -> Path:
    path = SNAPSHOT_DIR / f"{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path
