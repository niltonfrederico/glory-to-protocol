from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.runner import _rejected_handle
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobCallback
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.jobs.types import JobStatus
from glory_to_protocol.jobs.types import RecursionPolicy
from glory_to_protocol.jobs.types import RollbackFn

_logger = logging.getLogger("glory_to_protocol.jobs")


@dataclass(slots=True)
class _Entry:
    job: Job
    handle: JobHandle
    rollback: RollbackFn | None
    on_success: JobCallback | None
    timeout: float | None


class PipelineFailed(Exception):
    """Raised when a job in a `PipelineRunner` pipeline fails.

    `failed` is the outcome of the job that broke the pipeline. `rolled_back`
    lists the labels of previously-completed jobs whose rollback was invoked
    (in LIFO order). `rollback_errors` collects any exceptions raised by
    rollback callbacks; those are logged and swallowed during execution so the
    full LIFO chain still runs.
    """

    def __init__(
        self,
        failed: JobOutcome,
        rolled_back: list[str],
        rollback_errors: list[tuple[str, BaseException]],
    ) -> None:
        super().__init__(f"pipeline failed at {failed.label!r}: {failed.error!r}")
        self.failed = failed
        self.rolled_back = rolled_back
        self.rollback_errors = rollback_errors


class PipelineRunner:
    """Async context manager that runs jobs sequentially, aborting on failure.

    Unlike `JobRunner` (fan-out, isolated failures), `PipelineRunner` treats the
    registered jobs as a transaction. `spawn` only records the job + callbacks;
    execution happens on context exit. The first failure stops the pipeline,
    triggers LIFO rollback of previously-completed jobs, marks unreached jobs
    as `"skipped"`, and re-raises as `PipelineFailed`.

    If the context body itself raises, no jobs run and the body's exception
    propagates unchanged (nothing to roll back).

    `max_children` caps registered jobs (0 = unbounded); exceeding the cap
    always raises. `on_recursion` governs `spawn` calls made after execution
    has started (e.g. from a callback): `"raise"` errors, `"warn"` logs and
    returns a synthetic skipped handle that is not enrolled in the pipeline.
    """

    def __init__(
        self,
        *,
        max_children: int = 12,
        on_recursion: RecursionPolicy | str = RecursionPolicy.RAISE,
    ) -> None:
        if max_children < 0:
            raise ValueError("max_children must be >= 0 (0 means unbounded)")
        self._entries: list[_Entry] = []
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
        if exc_type is not None:
            self._closing = True
            return
        if not self._entries:
            self._closing = True
            return

        self._closing = True

        completed: list[_Entry] = []
        failed_entry: _Entry | None = None

        for entry in self._entries:
            outcome = await self._run_one(entry)
            if outcome.status is JobStatus.OK:
                completed.append(entry)
                continue
            failed_entry = entry
            break

        if failed_entry is None:
            return

        idx = self._entries.index(failed_entry)
        for entry in self._entries[idx + 1 :]:
            entry.handle.status = JobStatus.SKIPPED
            entry.handle.outcome = JobOutcome(
                label=entry.job.label,
                status=JobStatus.SKIPPED,
                error=None,
                duration_ms=0,
            )

        rolled_back: list[str] = []
        rollback_errors: list[tuple[str, BaseException]] = []
        for entry in reversed(completed):
            if entry.rollback is None:
                continue
            assert entry.handle.outcome is not None
            try:
                await entry.rollback(entry.handle.outcome)
                rolled_back.append(entry.job.label)
            except Exception as rb_err:
                _logger.warning(
                    "rollback failed: label=%r error=%r",
                    entry.job.label,
                    rb_err,
                )
                rollback_errors.append((entry.job.label, rb_err))

        assert failed_entry.handle.outcome is not None
        raise PipelineFailed(
            failed=failed_entry.handle.outcome,
            rolled_back=rolled_back,
            rollback_errors=rollback_errors,
        )

    def spawn(
        self,
        job: Job,
        *,
        rollback: RollbackFn | None = None,
        on_success: JobCallback | None = None,
        timeout: float | None = None,
    ) -> JobHandle:
        if not self._entered:
            raise RuntimeError("PipelineRunner.spawn called outside of async context")
        if self._closing:
            reason = "spawn called after pipeline started (callback recursion)"
            if self._on_recursion is RecursionPolicy.RAISE:
                raise RuntimeError(f"PipelineRunner.spawn rejected: {reason}")
            return _rejected_handle(job.label, reason)
        if self._max_children > 0 and len(self._entries) >= self._max_children:
            raise RuntimeError(
                f"PipelineRunner.spawn rejected: max_children={self._max_children} reached"
            )
        handle = JobHandle(label=job.label)
        self._entries.append(
            _Entry(
                job=job,
                handle=handle,
                rollback=rollback,
                on_success=on_success,
                timeout=timeout,
            )
        )
        return handle

    @property
    def handles(self) -> list[JobHandle]:
        return [e.handle for e in self._entries]

    @property
    def outcomes(self) -> list[JobOutcome]:
        return [e.handle.outcome for e in self._entries if e.handle.outcome is not None]

    async def _run_one(self, entry: _Entry) -> JobOutcome:
        job = entry.job
        handle = entry.handle
        start = time.monotonic()
        error: Exception | None = None
        try:
            if entry.timeout is None:
                await job.coro_factory()
            else:
                await asyncio.wait_for(job.coro_factory(), entry.timeout)
        except Exception as err:
            error = err
        duration_ms = int((time.monotonic() - start) * 1000)
        status = JobStatus.FAIL if error is not None else JobStatus.OK
        outcome = JobOutcome(label=job.label, status=status, error=error, duration_ms=duration_ms)
        handle.outcome = outcome
        handle.status = status
        if error is not None:
            _logger.warning(
                "pipeline job failed: label=%r duration_ms=%d error=%r",
                job.label,
                duration_ms,
                error,
            )
        else:
            _logger.info("pipeline job ok: label=%r duration_ms=%d", job.label, duration_ms)
            if entry.on_success is not None:
                try:
                    await entry.on_success(outcome)
                except Exception as cb_err:
                    _logger.warning(
                        "on_success failed: label=%r error=%r",
                        job.label,
                        cb_err,
                    )
        return outcome
