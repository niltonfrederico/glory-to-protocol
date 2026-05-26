from __future__ import annotations

from typing import Literal

from rich.console import Console

from glory_to_protocol.registry import ExposedCommand
from glory_to_protocol.tui.stamps import stamp_approve
from glory_to_protocol.tui.stamps import stamp_reject

ResultOutcome = Literal["approved", "rejected"]


def render_result_stamp(
    command: ExposedCommand,
    outcome: str,
    *,
    detail: str = "",
    console: Console | None = None,
) -> None:
    """Print an official stamp summarizing the command outcome to the console.

    Called after `protocol.run()` dispatches the callback; the stamp lives
    outside the alt-screen Textual surface so it persists in scrollback.
    """
    active = console or Console(highlight=False, soft_wrap=False)
    label = command.label
    stamp = stamp_approve(label, detail) if outcome == "approved" else stamp_reject(label, detail)
    active.print(stamp)
