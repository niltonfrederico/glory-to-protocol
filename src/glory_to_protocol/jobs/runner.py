from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.jobs.types import JobStatus

_logger = logging.getLogger("glory_to_protocol.jobs")


@dataclass(slots=True)
class JobHandle:
    """Mutable handle exposed to observers (TUI region).

    `status` flips from `"pending"` to the terminal state when the underlying
    task finishes. `outcome` is set at the same time.
    """

    label: str
    status: JobStatus = "pending"
    outcome: JobOutcome | None = None

    def done(self) -> bool:
        return self.status != "pending"


class JobRunner:
    """Async context manager that fans out independent background jobs.

    Failures are isolated: an exception in one job marks that job `fail` but
    never cancels siblings or propagates out of `__aexit__`. Outcomes are
    collected in registration order via the `outcomes` property.

    Cancellation propagates: a job task receiving `CancelledError` is not
    converted into a `"fail"` outcome; it stays `pending` and the
    `CancelledError` flows up through `__aexit__`. If the context body raises,
    pending tasks are cancelled before waiting on `gather`.
    """

    def __init__(self) -> None:
        self._handles: list[JobHandle] = []
        self._tasks: list[asyncio.Task[None]] = []
        self._entered = False

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
        if exc_type is not None:
            for task in self._tasks:
                task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

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
        return [h.outcome for h in self._handles if h.outcome is not None]

    async def _run(self, job: Job, handle: JobHandle) -> None:
        start = time.monotonic()
        error: Exception | None = None
        try:
            await job.coro_factory()
        except Exception as err:
            error = err
        duration_ms = int((time.monotonic() - start) * 1000)
        status: JobStatus = "fail" if error is not None else "ok"
        outcome = JobOutcome(label=job.label, status=status, error=error, duration_ms=duration_ms)
        handle.outcome = outcome
        handle.status = status
        if error is not None:
            _logger.warning(
                "job failed: label=%r duration_ms=%d error=%r",
                job.label,
                duration_ms,
                error,
            )
        else:
            _logger.info("job ok: label=%r duration_ms=%d", job.label, duration_ms)
