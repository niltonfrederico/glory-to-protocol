from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobCallback
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.jobs.types import JobStatus
from glory_to_protocol.jobs.types import RecursionPolicy
from glory_to_protocol.jobs.types import RollbackFn

_logger = logging.getLogger("glory_to_protocol.jobs")


@dataclass(slots=True)
class JobHandle:
    """Mutable handle exposed to observers (TUI region).

    `status` flips from `JobStatus.PENDING` to the terminal state when the
    underlying task finishes. `outcome` is set at the same time.
    """

    label: str
    status: JobStatus = JobStatus.PENDING
    outcome: JobOutcome | None = None

    def done(self) -> bool:
        return self.status is not JobStatus.PENDING


def _rejected_handle(label: str, reason: str) -> JobHandle:
    """Synthetic handle returned when spawn is rejected in `warn` mode."""
    outcome = JobOutcome(label=label, status=JobStatus.SKIPPED, error=None, duration_ms=0)
    handle = JobHandle(label=label, status=JobStatus.SKIPPED, outcome=outcome)
    _logger.warning("spawn rejected: label=%r reason=%s", label, reason)
    return handle


class JobRunner:
    """Async context manager that fans out independent background jobs.

    Failures are isolated: an exception in one job marks that job `fail` but
    never cancels siblings or propagates out of `__aexit__`. Outcomes are
    collected in registration order via the `outcomes` property.

    Cancellation propagates: a job task receiving `CancelledError` is not
    converted into a `"fail"` outcome; it stays `pending` and the
    `CancelledError` flows up through `__aexit__`. If the context body raises,
    pending tasks are cancelled before waiting on `gather`.

    `max_children` caps the number of jobs that can be spawned (0 = unbounded).
    Exceeding the cap always raises — it indicates a programmer error. The
    `on_recursion` policy controls what happens when `spawn` is called after
    `__aexit__` has begun (e.g. from inside a callback): `"raise"` surfaces a
    `RuntimeError`, `"warn"` logs and returns a synthetic skipped handle.
    """

    def __init__(
        self,
        *,
        max_children: int = 12,
        on_recursion: RecursionPolicy | str = RecursionPolicy.RAISE,
    ) -> None:
        if max_children < 0:
            raise ValueError("max_children must be >= 0 (0 means unbounded)")
        self._handles: list[JobHandle] = []
        self._tasks: list[asyncio.Task[None]] = []
        self._entered = False
        self._closing = False
        self._max_children = max_children
        self._on_recursion = RecursionPolicy(on_recursion)

    async def __aenter__(self) -> Self:
        self._entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _tb: TracebackType | None,
    ) -> None:
        self._closing = True
        if not self._tasks:
            return
        if exc_type is not None:
            for task in self._tasks:
                task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    def spawn(
        self,
        job: Job,
        *,
        rollback: RollbackFn | None = None,
        on_success: JobCallback | None = None,
        timeout: float | None = None,
    ) -> JobHandle:
        if not self._entered:
            raise RuntimeError("JobRunner.spawn called outside of async context")
        if self._closing:
            reason = "spawn called after context exit (callback recursion)"
            if self._on_recursion is RecursionPolicy.RAISE:
                raise RuntimeError(f"JobRunner.spawn rejected: {reason}")
            return _rejected_handle(job.label, reason)
        if self._max_children > 0 and len(self._handles) >= self._max_children:
            raise RuntimeError(
                f"JobRunner.spawn rejected: max_children={self._max_children} reached"
            )
        handle = JobHandle(label=job.label)
        task = asyncio.create_task(
            self._run(job, handle, rollback, on_success, timeout),
            name=f"job:{job.label}",
        )
        self._handles.append(handle)
        self._tasks.append(task)
        return handle

    @property
    def handles(self) -> list[JobHandle]:
        return list(self._handles)

    @property
    def outcomes(self) -> list[JobOutcome]:
        return [h.outcome for h in self._handles if h.outcome is not None]

    async def _run(
        self,
        job: Job,
        handle: JobHandle,
        rollback: RollbackFn | None,
        on_success: JobCallback | None,
        timeout: float | None,
    ) -> None:
        start = time.monotonic()
        error: Exception | None = None
        try:
            if timeout is None:
                await job.coro_factory()
            else:
                await asyncio.wait_for(job.coro_factory(), timeout)
        except Exception as err:
            error = err
        duration_ms = int((time.monotonic() - start) * 1000)
        status = JobStatus.FAIL if error is not None else JobStatus.OK
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
            if rollback is not None:
                try:
                    await rollback(outcome)
                except Exception as rb_err:
                    _logger.warning(
                        "rollback failed: label=%r error=%r",
                        job.label,
                        rb_err,
                    )
        else:
            _logger.info("job ok: label=%r duration_ms=%d", job.label, duration_ms)
            if on_success is not None:
                try:
                    await on_success(outcome)
                except Exception as cb_err:
                    _logger.warning(
                        "on_success failed: label=%r error=%r",
                        job.label,
                        cb_err,
                    )
