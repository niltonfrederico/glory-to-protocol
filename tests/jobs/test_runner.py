from __future__ import annotations

import asyncio

import pytest

from glory_to_protocol.jobs.runner import JobHandle
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


async def test_should_invoke_on_success_when_job_succeeds() -> None:
    seen: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def after(outcome):  # type: ignore[no-untyped-def]
        seen.append(outcome.label)

    async with JobRunner() as runner:
        runner.spawn(Job("good", ok), on_success=after)

    assert seen == ["good"]


async def test_should_skip_on_success_when_job_fails() -> None:
    seen: list[str] = []

    async def boom() -> None:
        raise RuntimeError("nope")

    async def after(outcome):  # type: ignore[no-untyped-def]
        seen.append(outcome.label)

    async with JobRunner() as runner:
        runner.spawn(Job("bad", boom), on_success=after)

    assert seen == []


async def test_should_log_and_swallow_when_on_success_raises() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async def bad_after(outcome):  # type: ignore[no-untyped-def]
        raise RuntimeError("callback exploded")

    async with JobRunner() as runner:
        runner.spawn(Job("good", ok), on_success=bad_after)

    [outcome] = runner.outcomes
    assert outcome.status == "ok"


async def test_should_fail_with_timeout_when_job_exceeds_timeout() -> None:
    async def slow() -> None:
        await asyncio.sleep(60)

    async with JobRunner() as runner:
        runner.spawn(Job("slow", slow), timeout=0.05)

    [outcome] = runner.outcomes
    assert outcome.status == "fail"
    assert isinstance(outcome.error, TimeoutError)


async def test_should_invoke_rollback_when_timeout_triggers_failure() -> None:
    undone: list[str] = []

    async def slow() -> None:
        await asyncio.sleep(60)

    async def undo(outcome):  # type: ignore[no-untyped-def]
        undone.append(outcome.label)

    async with JobRunner() as runner:
        runner.spawn(Job("slow", slow), timeout=0.05, rollback=undo)

    assert undone == ["slow"]


async def test_should_raise_when_max_children_exceeded() -> None:
    async def ok() -> None:
        await asyncio.sleep(0.01)

    async with JobRunner(max_children=2) as runner:
        runner.spawn(Job("a", ok))
        runner.spawn(Job("b", ok))
        with pytest.raises(RuntimeError, match="max_children=2"):
            runner.spawn(Job("c", ok))


async def test_should_allow_unbounded_spawn_when_max_children_zero() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async with JobRunner(max_children=0) as runner:
        for i in range(50):
            runner.spawn(Job(f"j{i}", ok))

    assert len(runner.outcomes) == 50


async def test_should_reject_with_skipped_handle_when_recursion_in_warn_mode() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    captured: dict[str, object] = {}

    async def callback(outcome):  # type: ignore[no-untyped-def]
        captured["handle"] = runner.spawn(Job("child", ok))

    runner = JobRunner(on_recursion="warn")
    async with runner:
        runner.spawn(Job("parent", ok), on_success=callback)

    child = captured["handle"]
    assert isinstance(child, JobHandle)
    assert child.status == "skipped"
    assert [h.label for h in runner.handles] == ["parent"]


def test_should_raise_when_max_children_negative() -> None:
    with pytest.raises(ValueError):
        JobRunner(max_children=-1)


async def test_should_allow_nested_job_runner_inside_callback() -> None:
    inner_outcomes: list[str] = []

    async def leaf() -> None:
        await asyncio.sleep(0)

    async def nested_runner_callback(outcome):  # type: ignore[no-untyped-def]
        async with JobRunner() as inner:
            inner.spawn(Job("child-a", leaf))
            inner.spawn(Job("child-b", leaf))
        inner_outcomes.extend(o.label for o in inner.outcomes)

    async with JobRunner() as outer:
        outer.spawn(Job("parent", leaf), on_success=nested_runner_callback)

    assert inner_outcomes == ["child-a", "child-b"]
    assert [o.status for o in outer.outcomes] == ["ok"]


async def test_should_raise_when_recursion_in_raise_mode() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    errors: list[BaseException] = []

    async def callback(outcome):  # type: ignore[no-untyped-def]
        try:
            runner.spawn(Job("child", ok))
        except RuntimeError as err:
            errors.append(err)

    runner = JobRunner(on_recursion="raise")
    async with runner:
        runner.spawn(Job("parent", ok), on_success=callback)

    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)
