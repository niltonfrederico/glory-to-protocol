from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class JobStatus(StrEnum):
    """Terminal state of a job (or `PENDING` while still running).

    `StrEnum` so existing string comparisons (`outcome.status == "ok"`) keep
    working; new code should prefer the enum members for clarity.
    """

    PENDING = "pending"
    OK = "ok"
    FAIL = "fail"
    SKIPPED = "skipped"


class RecursionPolicy(StrEnum):
    """How a runner reacts when `spawn` is called after the context starts
    closing — typically because a callback called `spawn` on the same runner.
    """

    RAISE = "raise"
    WARN = "warn"


JobCoroFactory = Callable[[], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class Job:
    """A unit of background work to run alongside a foreground task.

    `critical` is currently recorded but not acted upon; callers compute the
    foreground stamp independently of job outcomes. The flag exists so callers
    can already tag jobs (audit vs best-effort) without a later schema change.
    """

    label: str
    coro_factory: JobCoroFactory
    critical: bool = False


@dataclass(frozen=True, slots=True)
class JobOutcome:
    label: str
    status: JobStatus
    error: BaseException | None
    duration_ms: int


RollbackFn = Callable[[JobOutcome], Awaitable[None]]
JobCallback = Callable[[JobOutcome], Awaitable[None]]
