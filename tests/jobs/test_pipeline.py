from __future__ import annotations

import asyncio

import pytest

from glory_to_protocol.jobs.pipeline import PipelineFailed
from glory_to_protocol.jobs.pipeline import PipelineRunner
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome


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
