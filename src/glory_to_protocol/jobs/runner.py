from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from dataclasses import field
from types import TracebackType
from typing import Self

from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.jobs.types import JobStatus

_logger = logging.getLogger("glory_to_protocol.jobs")


@dataclass
class JobHandle:
    """Mutable handle exposed to observers (TUI region).

    `status` flips from `"pending"` to the terminal state when the underlying
    task finishes. `outcome` is set at the same time.
    """

    label: str
    status: JobStatus = "pending"
    outcome: JobOutcome | None = None
    _started_at: float = field(default_factory=time.monotonic)

    def done(self) -> bool:
        return self.status != "pending"


class JobRunner:
    """Async context manager that fans out independent background jobs.

    Failures are isolated: an exception in one job marks that job `fail` but
    never cancels siblings or propagates out of `__aexit__`. Outcomes are
    collected in registration order via the `outcomes` property.
    """

    def __init__(self) -> None:
        self._handles: list[JobHandle] = []
        self._tasks: list[asyncio.Task[None]] = []
        self._entered = False
        self._outcomes: list[JobOutcome] = []

    async def __aenter__(self) -> Self:
        self._entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if not self._tasks:
            return
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._outcomes = [handle.outcome for handle in self._handles if handle.outcome is not None]

    def spawn(self, job: Job) -> JobHandle:
        if not self._entered:
            raise RuntimeError("JobRunner.spawn called outside of async context")
        handle = JobHandle(label=job.label)
        task = asyncio.create_task(self._run(job, handle), name=f"job:{job.label}")
        self._handles.append(handle)
        self._tasks.append(task)
        return handle

    @property
    def handles(self) -> list[JobHandle]:
        return list(self._handles)

    @property
    def outcomes(self) -> list[JobOutcome]:
        return list(self._outcomes)

    async def _run(self, job: Job, handle: JobHandle) -> None:
        start = time.monotonic()
        try:
            await job.coro_factory()
        except BaseException as err:
            duration_ms = int((time.monotonic() - start) * 1000)
            outcome = JobOutcome(label=job.label, status="fail", error=err, duration_ms=duration_ms)
            handle.outcome = outcome
            handle.status = "fail"
            _logger.warning(
                "job failed: label=%r duration_ms=%d error=%r",
                job.label,
                duration_ms,
                err,
            )
            return
        duration_ms = int((time.monotonic() - start) * 1000)
        outcome = JobOutcome(label=job.label, status="ok", error=None, duration_ms=duration_ms)
        handle.outcome = outcome
        handle.status = "ok"
        _logger.info("job ok: label=%r duration_ms=%d", job.label, duration_ms)
