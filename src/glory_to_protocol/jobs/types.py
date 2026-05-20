from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

JobStatus = Literal["pending", "ok", "fail"]

JobCoroFactory = Callable[[], Awaitable[None]]


@dataclass(frozen=True)
class Job:
    """A unit of background work to run alongside a foreground task.

    `critical` is currently recorded but not acted upon; callers compute the
    foreground stamp independently of job outcomes. The flag exists so callers
    can already tag jobs (audit vs best-effort) without a later schema change.
    """

    label: str
    coro_factory: JobCoroFactory
    critical: bool = False


@dataclass(frozen=True)
class JobOutcome:
    label: str
    status: JobStatus
    error: BaseException | None
    duration_ms: int
