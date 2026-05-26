"""Pure interactive variant of the showcase.

Always tries the Textual surface first. In 0.3.0 the Textual app has not landed
yet, so the capability check returns "not implemented" and the Rich fallback
takes over (numbered palette + Rich prompts). In 0.4.0 the same binary will
open the live Textual shell instead — no code change required.

Run with `uv run protocol-tui`.
"""

from __future__ import annotations

from examples._shared import build_app
from glory_to_protocol import Mode
from glory_to_protocol import Protocol
from glory_to_protocol import ProtocolSettings

app = build_app()
protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.TUI),
)


def main() -> None:
    protocol.run()


if __name__ == "__main__":
    main()
