from __future__ import annotations

import asyncio

from rich.console import Console

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.jobs import _bordered_split


def test_should_truncate_left_when_bordered_split_overflows() -> None:
    long_left = "x" * (theme.FORM_WIDTH * 2)
    line = _bordered_split(long_left, "[★  OK  ★ ]", theme.STAMP_APPROVE)
    assert "║" in line.plain
    assert "[★  OK  ★ ]" in line.plain


async def test_should_drive_live_region_when_console_is_terminal() -> None:
    console = Console(
        record=True,
        width=theme.FORM_WIDTH,
        force_terminal=True,
        soft_wrap=False,
        highlight=False,
        legacy_windows=False,
    )
    with Form(title="t", console=console, show_header=False) as form:
        outcomes = await form.run_pending(
            [Job("live-tick", lambda: asyncio.sleep(0.4))],
        )
    result = [(o.label, o.status) for o in outcomes]
    assert result == [("live-tick", "ok")]


def test_should_render_pending_when_handle_status_pending() -> None:
    handle = JobHandle(label="pendência", status="pending")
    assert handle.done() is False
