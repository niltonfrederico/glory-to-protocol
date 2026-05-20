from __future__ import annotations

import asyncio

from rich.console import Console

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.jobs import render_pending_region


def _render(handles: list[JobHandle], phase: int) -> str:
    console = Console(
        record=True,
        width=theme.FORM_WIDTH,
        force_terminal=False,
        soft_wrap=False,
        highlight=False,
        legacy_windows=False,
    )
    console.print(render_pending_region(handles, phase))
    return console.export_text(clear=False)


def test_should_animate_trailing_dots_when_phase_increments() -> None:
    handle = JobHandle(label="aguardando carimbo")
    frame_0 = _render([handle], phase=0)
    frame_2 = _render([handle], phase=2)
    assert "aguardando carimbo" in frame_0
    assert "aguardando carimbo.." in frame_2
    assert "aguardando carimbo " in frame_0


def test_should_render_pending_mini_stamp_when_job_not_done() -> None:
    handle = JobHandle(label="anything")
    text = _render([handle], phase=0)
    assert "[★ ···  ★ ]" in text


def test_should_render_ok_mini_stamp_when_job_succeeded() -> None:
    handle = JobHandle(label="auditoria", status="ok")
    text = _render([handle], phase=0)
    assert "[★  OK  ★ ]" in text
    assert "auditoria." not in text


def test_should_render_fail_mini_stamp_when_job_failed() -> None:
    handle = JobHandle(label="ledger", status="fail")
    text = _render([handle], phase=3)
    assert "[★ FAIL ★ ]" in text
    assert "ledger." not in text


def test_should_right_align_mini_stamp_within_form_width() -> None:
    handle = JobHandle(label="x", status="ok")
    text = _render([handle], phase=0)
    lines = [line for line in text.splitlines() if line.strip()]
    stamp_line = lines[1]
    assert stamp_line.endswith("] ║"), repr(stamp_line)
    assert "★ ]" in stamp_line
    assert len(stamp_line) == theme.FORM_WIDTH


def test_should_complete_run_pending_when_fake_job_finishes() -> None:
    console = Console(
        record=True,
        width=theme.FORM_WIDTH,
        force_terminal=False,
        soft_wrap=False,
        highlight=False,
        legacy_windows=False,
    )

    async def scenario() -> list[tuple[str, str]]:
        with Form(title="t", console=console, show_header=False) as form:
            outcomes = await form.run_pending([Job("breve espera", lambda: asyncio.sleep(0.05))])
        return [(o.label, o.status) for o in outcomes]

    result = asyncio.run(scenario())
    assert result == [("breve espera", "ok")]
    rendered = console.export_text(clear=False)
    assert "breve espera" in rendered
    assert "[★  OK  ★ ]" in rendered


def test_should_return_empty_outcomes_when_no_jobs_passed_to_run_pending() -> None:
    console = Console(record=True, width=theme.FORM_WIDTH, force_terminal=False)

    async def scenario() -> list[object]:
        with Form(title="t", console=console, show_header=False) as form:
            return await form.run_pending([])

    assert asyncio.run(scenario()) == []
