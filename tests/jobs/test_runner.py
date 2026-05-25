from __future__ import annotations

import asyncio

import pytest

from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job


async def test_should_collect_two_ok_outcomes_when_both_jobs_succeed() -> None:
    async def ok_a() -> None:
        await asyncio.sleep(0)

    async def ok_b() -> None:
        await asyncio.sleep(0)

    async with JobRunner() as runner:
        runner.spawn(Job("alpha", ok_a))
        runner.spawn(Job("beta", ok_b))

    result = [(o.label, o.status) for o in runner.outcomes]
    assert result == [("alpha", "ok"), ("beta", "ok")]


async def test_should_mark_only_failing_job_when_one_raises() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("simulated failure")

    async with JobRunner() as runner:
        runner.spawn(Job("ok-job", ok))
        runner.spawn(Job("bad-job", boom))

    outcomes = [(o.label, o.status) for o in runner.outcomes]
    err = next(o.error for o in runner.outcomes if o.status == "fail")
    assert outcomes == [("ok-job", "ok"), ("bad-job", "fail")]
    assert isinstance(err, RuntimeError)
    assert str(err) == "simulated failure"


async def test_should_flip_handle_status_when_job_finishes() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def gated() -> None:
        started.set()
        await release.wait()

    async with JobRunner() as runner:
        handle = runner.spawn(Job("gated", gated))
        await started.wait()
        mid = handle.status
        release.set()
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        end = handle.status

    assert mid == "pending"
    assert end == "ok"


async def test_should_return_empty_outcomes_when_no_jobs_spawned() -> None:
    async with JobRunner() as runner:
        pass
    assert runner.outcomes == []


def test_should_raise_when_spawn_called_outside_async_context() -> None:
    runner = JobRunner()
    raised = False
    try:
        runner.spawn(Job("never", lambda: asyncio.sleep(0)))
    except RuntimeError:
        raised = True
    assert raised


async def test_should_propagate_cancellation_when_task_cancelled_externally() -> None:
    started = asyncio.Event()

    async def long_running() -> None:
        started.set()
        await asyncio.sleep(60)

    async def driver() -> None:
        async with JobRunner() as runner:
            runner.spawn(Job("long", long_running))
            await started.wait()

    task = asyncio.create_task(driver())
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_should_cancel_pending_tasks_when_context_body_raises() -> None:
    started = asyncio.Event()

    async def long_running() -> None:
        started.set()
        await asyncio.sleep(60)

    class Boom(RuntimeError):
        pass

    loop = asyncio.get_running_loop()
    t0 = loop.time()
    with pytest.raises(Boom):
        async with JobRunner() as runner:
            runner.spawn(Job("long-a", long_running))
            runner.spawn(Job("long-b", long_running))
            await started.wait()
            raise Boom("body fails")
    elapsed = loop.time() - t0
    assert elapsed < 1.0, f"__aexit__ blocked on pending tasks (elapsed={elapsed:.2f}s)"


async def test_should_not_mark_job_failed_when_task_cancelled() -> None:
    started = asyncio.Event()

    async def long_running() -> None:
        started.set()
        await asyncio.sleep(60)

    class Boom(RuntimeError):
        pass

    handle = None
    with pytest.raises(Boom):
        async with JobRunner() as runner:
            handle = runner.spawn(Job("cancellable", long_running))
            await started.wait()
            raise Boom("trigger cancellation in __aexit__")

    assert handle is not None
    assert handle.status != "fail", f"cancelled task was reported as fail: {handle.outcome}"


async def test_should_mark_job_failed_when_regular_exception_raised() -> None:
    async def boom() -> None:
        raise ValueError("boom")

    async with JobRunner() as runner:
        runner.spawn(Job("bad", boom))

    [outcome] = runner.outcomes
    assert outcome.status == "fail"
    assert isinstance(outcome.error, ValueError)


async def test_should_invoke_rollback_when_job_fails() -> None:
    seen: list[str] = []

    async def boom() -> None:
        raise RuntimeError("nope")

    async def undo(outcome):  # type: ignore[no-untyped-def]
        seen.append(outcome.label)

    async with JobRunner() as runner:
        runner.spawn(Job("bad", boom), rollback=undo)

    assert seen == ["bad"]


async def test_should_skip_rollback_when_job_succeeds() -> None:
    seen: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def undo(outcome):  # type: ignore[no-untyped-def]
        seen.append(outcome.label)

    async with JobRunner() as runner:
        runner.spawn(Job("good", ok), rollback=undo)

    assert seen == []


async def test_should_skip_rollback_when_job_cancelled() -> None:
    started = asyncio.Event()
    seen: list[str] = []

    async def long_running() -> None:
        started.set()
        await asyncio.sleep(60)

    async def undo(outcome):  # type: ignore[no-untyped-def]
        seen.append(outcome.label)

    class Boom(RuntimeError):
        pass

    with pytest.raises(Boom):
        async with JobRunner() as runner:
            runner.spawn(Job("cancellable", long_running), rollback=undo)
            await started.wait()
            raise Boom("body fails")

    assert seen == []


async def test_should_log_and_swallow_when_rollback_raises() -> None:
    async def boom() -> None:
        raise RuntimeError("primary")

    async def bad_undo(outcome):  # type: ignore[no-untyped-def]
        raise RuntimeError("rollback exploded")

    async with JobRunner() as runner:
        runner.spawn(Job("bad", boom), rollback=bad_undo)

    [outcome] = runner.outcomes
    assert outcome.status == "fail"
    assert isinstance(outcome.error, RuntimeError)
    assert str(outcome.error) == "primary"
