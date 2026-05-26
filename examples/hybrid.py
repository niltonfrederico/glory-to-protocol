"""Hybrid variant of the showcase.

If `argv` names a subcommand (`protocol-hybrid logo`, `protocol-hybrid jobs`),
dispatches as a Typer CLI. Bare `protocol-hybrid` tries the Textual surface;
since 0.3.0 ships without it, the Rich fallback engages instead.

Run with:
- `uv run protocol-hybrid` → interactive fallback (palette + prompts)
- `uv run protocol-hybrid [logo|palette|wrap|jobs|stamps]` → CLI dispatch
"""

from __future__ import annotations

from examples._shared import build_app
from glory_to_protocol import Mode
from glory_to_protocol import Protocol
from glory_to_protocol import ProtocolSettings

app = build_app()
protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.HYBRID),
)


def main() -> None:
    protocol.run()


if __name__ == "__main__":
    main()
