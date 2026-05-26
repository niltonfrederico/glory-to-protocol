"""Pure CLI variant of the showcase.

Always dispatches as a Typer CLI — never tries the Textual surface, never
falls back to the Rich palette. Use this shape when the binary is meant to be
scriptable and headless (CI, pipelines, cron).

Run with `uv run protocol-cli [logo|palette|wrap|jobs|stamps]`.
"""

from __future__ import annotations

from examples._shared import build_app
from glory_to_protocol import Mode
from glory_to_protocol import Protocol
from glory_to_protocol import ProtocolSettings

app = build_app()
protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.CLI),
)


def main() -> None:
    protocol.run()


if __name__ == "__main__":
    main()
