import asyncio

from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job


def test_should_return_copy_of_handles_when_handles_property_accessed() -> None:
    async def runner() -> tuple[int, int]:
        async with JobRunner() as r:
            r.spawn(Job(label="noop", coro_factory=lambda: asyncio.sleep(0)))
            snapshot = len(r.handles)
            r.spawn(Job(label="noop2", coro_factory=lambda: asyncio.sleep(0)))
            return snapshot, len(r.handles)

    before, after = asyncio.run(runner())
    assert before == 1
    assert after == 2
