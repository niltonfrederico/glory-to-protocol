from __future__ import annotations

import asyncio
import contextlib
from types import TracebackType
from typing import Self

from rich.console import Console
from rich.console import Group
from rich.live import Live
from rich.style import Style
from rich.text import Text

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.types import JobStatus
from glory_to_protocol.tui import theme
from glory_to_protocol.tui._borders import bordered_line
from glory_to_protocol.tui._borders import bordered_split

_TICK_SECONDS = 0.25
_REFRESH_PER_SECOND = 4

_DOT_FRAMES = ("", ".", "..", "...")

_MINI_STAMP_INNER = 4


def _mini_stamp(label: str) -> str:
    return f"[★ {label.center(_MINI_STAMP_INNER)} ★ ]"


_MINI_STAMP: dict[JobStatus, tuple[str, Style]] = {
    "pending": (_mini_stamp("···"), theme.MUTED),
    "ok": (_mini_stamp("OK"), theme.STAMP_APPROVE),
    "fail": (_mini_stamp("FAIL"), theme.STAMP_REJECT),
}


def _label_with_dots(label: str, phase: int, done: bool) -> str:
    if done:
        return label
    return label + _DOT_FRAMES[phase % len(_DOT_FRAMES)]


def render_pending_region(handles: list[JobHandle], phase: int) -> Group:
    """Render the full pending-jobs region as a Rich Group.

    Two bordered lines per job: the label (with animated trailing dots while
    pending) and a right-aligned mini-stamp. Pure function — easy to snapshot
    in tests without spinning up Live.
    """
    parts: list[Text] = []
    for handle in handles:
        status: JobStatus = handle.status
        done = status != "pending"
        stamp_text, stamp_style = _MINI_STAMP[status]

        parts.append(bordered_line(_label_with_dots(handle.label, phase, done)))
        parts.append(bordered_split("", stamp_text, stamp_style))
    return Group(*parts)


class PendingJobsRegion:
    """Async context manager that renders job handles as a live region.

    Opens a `rich.live.Live` while the foreground task awaits the runner.
    Ticks a phase counter every 250ms to animate the trailing dots. When the
    context exits, leaves the final rendered state in the buffer so the form
    keeps printing below it.
    """

    def __init__(self, console: Console, handles: list[JobHandle]) -> None:
        self._console = console
        self._handles = handles
        self._phase = 0
        self._live: Live | None = None
        self._ticker: asyncio.Task[None] | None = None

    async def __aenter__(self) -> Self:
        if self._console.is_terminal:
            self._live = Live(
                self._make_renderable(),
                console=self._console,
                refresh_per_second=_REFRESH_PER_SECOND,
                transient=True,
            )
            self._live.__enter__()
        self._ticker = asyncio.create_task(self._loop(), name="pending-region-ticker")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._ticker is not None and not self._ticker.done():
            self._ticker.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ticker
        self._ticker = None
        if self._live is not None:
            self._live.__exit__(None, None, None)
            self._live = None
        self._console.print(self._make_renderable())

    async def wait(self) -> None:
        """Block until every job reaches a terminal state.

        Drives the body of the `async with` so the caller can `await` and let
        the live region tick in the meantime. Safe to call exactly once per
        region — exits when the ticker loop sees `_all_done()`.
        """
        if self._ticker is None:
            return
        with contextlib.suppress(asyncio.CancelledError):
            await self._ticker

    async def _loop(self) -> None:
        while not self._all_done():
            await asyncio.sleep(_TICK_SECONDS)
            self._phase = (self._phase + 1) % len(_DOT_FRAMES)
            if self._live is not None:
                self._live.update(self._make_renderable())

    def _all_done(self) -> bool:
        return all(h.done() for h in self._handles)

    def _make_renderable(self) -> Group:
        return render_pending_region(self._handles, self._phase)
