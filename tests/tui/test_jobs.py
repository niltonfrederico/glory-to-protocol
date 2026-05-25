from __future__ import annotations

import asyncio

import pytest
from rich.console import Console

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobStatus
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.jobs import render_pending_region


def _render(handles: list[JobHandle], phase: int, console: Console) -> str:
    console.print(render_pending_region(handles, phase))
    return console.export_text(clear=False)


def test_should_animate_trailing_dots_when_phase_increments(snapshot_console: Console) -> None:
    handle = JobHandle(label="aguardando carimbo")
    frame_0 = _render([handle], phase=0, console=snapshot_console)
    frame_2 = _render([handle], phase=2, console=snapshot_console)
    assert "aguardando carimbo" in frame_0
    assert "aguardando carimbo.." in frame_2
    assert "aguardando carimbo " in frame_0


@pytest.mark.parametrize(
    ("handle", "expected_stamp"),
    [
        (JobHandle(label="anything"), "[★ ···  ★ ]"),
        (JobHandle(label="auditoria", status=JobStatus.OK), "[★  OK  ★ ]"),
        (JobHandle(label="ledger", status=JobStatus.FAIL), "[★ FAIL ★ ]"),
    ],
)
def test_should_render_mini_stamp_matching_status_when_job_rendered(
    snapshot_console: Console, handle: JobHandle, expected_stamp: str
) -> None:
    text = _render([handle], phase=0, console=snapshot_console)
    assert expected_stamp in text
    if handle.status != "pending":
        assert f"{handle.label}." not in text


def test_should_right_align_mini_stamp_within_form_width(snapshot_console: Console) -> None:
    handle = JobHandle(label="x", status=JobStatus.OK)
    text = _render([handle], phase=0, console=snapshot_console)
    lines = [line for line in text.splitlines() if line.strip()]
    stamp_line = lines[1]
    assert stamp_line.endswith("] ║"), repr(stamp_line)
    assert "★ ]" in stamp_line
    assert len(stamp_line) == theme.FORM_WIDTH


async def test_should_complete_run_pending_when_fake_job_finishes(
    snapshot_console: Console,
) -> None:
    with Form(title="t", console=snapshot_console, show_header=False) as form:
        outcomes = await form.run_pending([Job("breve espera", lambda: asyncio.sleep(0.05))])
    result = [(o.label, o.status) for o in outcomes]
    assert result == [("breve espera", "ok")]
    rendered = snapshot_console.export_text(clear=False)
    assert "breve espera" in rendered
    assert "[★  OK  ★ ]" in rendered


async def test_should_return_empty_outcomes_when_no_jobs_passed_to_run_pending(
    snapshot_console: Console,
) -> None:
    with Form(title="t", console=snapshot_console, show_header=False) as form:
        outcomes = await form.run_pending([])
    assert outcomes == []
