from __future__ import annotations

import asyncio

from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome


def test_should_collect_two_ok_outcomes_when_both_jobs_succeed() -> None:
    async def ok_a() -> None:
        await asyncio.sleep(0)

    async def ok_b() -> None:
        await asyncio.sleep(0)

    async def scenario() -> list[tuple[str, str]]:
        async with JobRunner() as runner:
            runner.spawn(Job("alpha", ok_a))
            runner.spawn(Job("beta", ok_b))
        return [(o.label, o.status) for o in runner.outcomes]

    result = asyncio.run(scenario())
    assert result == [("alpha", "ok"), ("beta", "ok")]


def test_should_mark_only_failing_job_when_one_raises() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("simulated failure")

    async def scenario() -> tuple[list[tuple[str, str]], BaseException | None]:
        async with JobRunner() as runner:
            runner.spawn(Job("ok-job", ok))
            runner.spawn(Job("bad-job", boom))
        outcomes: list[tuple[str, str]] = [(o.label, o.status) for o in runner.outcomes]
        err = next(o.error for o in runner.outcomes if o.status == "fail")
        return outcomes, err

    outcomes, err = asyncio.run(scenario())
    assert outcomes == [("ok-job", "ok"), ("bad-job", "fail")]
    assert isinstance(err, RuntimeError)
    assert str(err) == "simulated failure"


def test_should_flip_handle_status_when_job_finishes() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def gated() -> None:
        started.set()
        await release.wait()

    async def scenario() -> list[str]:
        async with JobRunner() as runner:
            handle = runner.spawn(Job("gated", gated))
            await started.wait()
            mid = handle.status
            release.set()
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            end = handle.status
            return [mid, end]

    states = asyncio.run(scenario())
    assert states[0] == "pending"
    assert states[1] == "ok"


def test_should_return_empty_outcomes_when_no_jobs_spawned() -> None:
    async def scenario() -> list[JobOutcome]:
        async with JobRunner() as runner:
            pass
        return runner.outcomes

    assert asyncio.run(scenario()) == []


def test_should_raise_when_spawn_called_outside_async_context() -> None:
    runner = JobRunner()
    raised = False
    try:
        runner.spawn(Job("never", lambda: asyncio.sleep(0)))
    except RuntimeError:
        raised = True
    assert raised
