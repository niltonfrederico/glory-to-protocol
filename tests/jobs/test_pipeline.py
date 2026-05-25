from __future__ import annotations

import asyncio

import pytest

from glory_to_protocol.jobs.pipeline import PipelineFailed
from glory_to_protocol.jobs.pipeline import PipelineRunner
from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome


async def test_should_noop_when_pipeline_has_no_jobs() -> None:
    async with PipelineRunner() as p:
        pass
    assert p.outcomes == []


async def test_should_log_and_swallow_when_pipeline_on_success_raises() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async def bad_after(outcome: JobOutcome) -> None:
        raise RuntimeError("callback exploded")

    async with PipelineRunner() as p:
        p.spawn(Job("good", ok), on_success=bad_after)

    [outcome] = p.outcomes
    assert outcome.status == "ok"


async def test_should_run_jobs_in_order_when_all_succeed() -> None:
    order: list[str] = []

    async def make(label: str):  # type: ignore[no-untyped-def]
        async def _coro() -> None:
            order.append(label)

        return _coro

    async with PipelineRunner() as p:
        p.spawn(Job("a", await make("a")))
        p.spawn(Job("b", await make("b")))
        p.spawn(Job("c", await make("c")))

    assert order == ["a", "b", "c"]
    assert [o.status for o in p.outcomes] == ["ok", "ok", "ok"]


async def test_should_abort_remaining_when_a_job_fails() -> None:
    order: list[str] = []

    async def ok_a() -> None:
        order.append("a")

    async def boom() -> None:
        order.append("b")
        raise RuntimeError("nope")

    async def ok_c() -> None:
        order.append("c")

    with pytest.raises(PipelineFailed):
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok_a))
            p.spawn(Job("b", boom))
            p.spawn(Job("c", ok_c))

    assert order == ["a", "b"]


async def test_should_rollback_completed_lifo_when_a_job_fails() -> None:
    undone: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("nope")

    def make_undo(label: str):  # type: ignore[no-untyped-def]
        async def _undo(outcome: JobOutcome) -> None:
            undone.append(label)

        return _undo

    with pytest.raises(PipelineFailed) as exc_info:
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok), rollback=make_undo("a"))
            p.spawn(Job("b", ok), rollback=make_undo("b"))
            p.spawn(Job("c", boom), rollback=make_undo("c"))
            p.spawn(Job("d", ok), rollback=make_undo("d"))

    assert undone == ["b", "a"]
    assert exc_info.value.rolled_back == ["b", "a"]


async def test_should_mark_unreached_as_skipped_when_a_job_fails() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("nope")

    with pytest.raises(PipelineFailed):
        async with PipelineRunner() as p:
            h_a = p.spawn(Job("a", ok))
            h_b = p.spawn(Job("b", boom))
            h_c = p.spawn(Job("c", ok))
            h_d = p.spawn(Job("d", ok))

    assert h_a.status == "ok"
    assert h_b.status == "fail"
    assert h_c.status == "skipped"
    assert h_d.status == "skipped"


async def test_should_raise_pipeline_failed_when_a_job_fails() -> None:
    async def boom() -> None:
        raise ValueError("kaboom")

    with pytest.raises(PipelineFailed) as exc_info:
        async with PipelineRunner() as p:
            p.spawn(Job("only", boom))

    assert exc_info.value.failed.label == "only"
    assert isinstance(exc_info.value.failed.error, ValueError)


async def test_should_continue_rollback_chain_when_one_rollback_raises() -> None:
    undone: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("trigger")

    async def good_undo_a(outcome: JobOutcome) -> None:
        undone.append("a")

    async def bad_undo_b(outcome: JobOutcome) -> None:
        raise RuntimeError("rollback for b exploded")

    with pytest.raises(PipelineFailed) as exc_info:
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok), rollback=good_undo_a)
            p.spawn(Job("b", ok), rollback=bad_undo_b)
            p.spawn(Job("c", boom))

    assert undone == ["a"]
    assert exc_info.value.rolled_back == ["a"]
    labels = [label for label, _ in exc_info.value.rollback_errors]
    assert labels == ["b"]


async def test_should_not_rollback_when_first_job_fails() -> None:
    undone: list[str] = []

    async def boom() -> None:
        raise RuntimeError("nope")

    async def undo(outcome: JobOutcome) -> None:
        undone.append(outcome.label)

    with pytest.raises(PipelineFailed) as exc_info:
        async with PipelineRunner() as p:
            p.spawn(Job("first", boom), rollback=undo)
            p.spawn(Job("second", boom), rollback=undo)

    assert undone == []
    assert exc_info.value.rolled_back == []


def test_should_raise_when_spawn_called_outside_async_context() -> None:
    p = PipelineRunner()
    with pytest.raises(RuntimeError):
        p.spawn(Job("never", lambda: asyncio.sleep(0)))


async def test_should_invoke_on_success_when_pipeline_job_succeeds() -> None:
    seen: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def after(outcome: JobOutcome) -> None:
        seen.append(outcome.label)

    async with PipelineRunner() as p:
        p.spawn(Job("a", ok), on_success=after)
        p.spawn(Job("b", ok), on_success=after)

    assert seen == ["a", "b"]


async def test_should_skip_on_success_for_unreached_pipeline_jobs() -> None:
    seen: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def boom() -> None:
        raise RuntimeError("nope")

    async def after(outcome: JobOutcome) -> None:
        seen.append(outcome.label)

    with pytest.raises(PipelineFailed):
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok), on_success=after)
            p.spawn(Job("b", boom), on_success=after)
            p.spawn(Job("c", ok), on_success=after)

    assert seen == ["a"]


async def test_should_fail_pipeline_with_timeout_when_job_exceeds_timeout() -> None:
    async def slow() -> None:
        await asyncio.sleep(60)

    with pytest.raises(PipelineFailed) as exc_info:
        async with PipelineRunner() as p:
            p.spawn(Job("slow", slow), timeout=0.05)

    assert isinstance(exc_info.value.failed.error, TimeoutError)


async def test_should_trigger_lifo_rollback_when_pipeline_job_times_out() -> None:
    undone: list[str] = []

    async def ok() -> None:
        await asyncio.sleep(0)

    async def slow() -> None:
        await asyncio.sleep(60)

    async def undo_a(outcome: JobOutcome) -> None:
        undone.append("a")

    async def undo_b(outcome: JobOutcome) -> None:
        undone.append("b")

    with pytest.raises(PipelineFailed):
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok), rollback=undo_a)
            p.spawn(Job("b", slow), rollback=undo_b, timeout=0.05)

    assert undone == ["a"]


async def test_should_raise_when_pipeline_max_children_exceeded() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async with PipelineRunner(max_children=2) as p:
        p.spawn(Job("a", ok))
        p.spawn(Job("b", ok))
        with pytest.raises(RuntimeError, match="max_children=2"):
            p.spawn(Job("c", ok))


async def test_should_allow_unbounded_pipeline_when_max_children_zero() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    async with PipelineRunner(max_children=0) as p:
        for i in range(50):
            p.spawn(Job(f"j{i}", ok))

    assert len(p.outcomes) == 50


async def test_should_reject_pipeline_recursion_with_skipped_in_warn_mode() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    captured: dict[str, object] = {}

    async def callback(outcome: JobOutcome) -> None:
        captured["handle"] = p.spawn(Job("child", ok))

    p = PipelineRunner(on_recursion="warn")
    async with p:
        p.spawn(Job("parent", ok), on_success=callback)

    child = captured["handle"]
    assert isinstance(child, JobHandle)
    assert child.status == "skipped"
    assert [h.label for h in p.handles] == ["parent"]


async def test_should_raise_on_pipeline_recursion_in_raise_mode() -> None:
    async def ok() -> None:
        await asyncio.sleep(0)

    errors: list[BaseException] = []

    async def callback(outcome: JobOutcome) -> None:
        try:
            p.spawn(Job("child", ok))
        except RuntimeError as err:
            errors.append(err)

    p = PipelineRunner(on_recursion="raise")
    async with p:
        p.spawn(Job("parent", ok), on_success=callback)

    assert len(errors) == 1


def test_should_raise_when_max_children_negative() -> None:
    with pytest.raises(ValueError):
        PipelineRunner(max_children=-1)


async def test_should_allow_nested_pipeline_runner_inside_callback() -> None:
    inner_outcomes: list[str] = []

    async def leaf() -> None:
        await asyncio.sleep(0)

    async def nested_pipeline_callback(outcome: JobOutcome) -> None:
        async with PipelineRunner() as inner:
            inner.spawn(Job("child-a", leaf))
            inner.spawn(Job("child-b", leaf))
        inner_outcomes.extend(o.label for o in inner.outcomes)

    async with PipelineRunner() as outer:
        outer.spawn(Job("parent", leaf), on_success=nested_pipeline_callback)

    assert inner_outcomes == ["child-a", "child-b"]
    assert [o.status for o in outer.outcomes] == ["ok"]


async def test_should_skip_execution_when_context_body_raises() -> None:
    ran: list[str] = []

    async def ok() -> None:
        ran.append("a")

    class Boom(RuntimeError):
        pass

    with pytest.raises(Boom):
        async with PipelineRunner() as p:
            p.spawn(Job("a", ok))
            raise Boom("body fails before execution")

    assert ran == []
