from __future__ import annotations

from datetime import UTC
from datetime import datetime
from types import TracebackType
from typing import Self

from rich.cells import cell_len
from rich.console import Console
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.settings import get_settings
from glory_to_protocol.tui import theme
from glory_to_protocol.tui._borders import bordered_line
from glory_to_protocol.tui._borders import inner_width
from glory_to_protocol.tui._borders import print_bordered_renderable
from glory_to_protocol.tui._borders import print_bottom
from glory_to_protocol.tui._borders import print_divider
from glory_to_protocol.tui._borders import print_top
from glory_to_protocol.tui._borders import truncate_to
from glory_to_protocol.tui.header import render_header
from glory_to_protocol.tui.jobs import PendingJobsRegion


def _wrap_cells(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    out: list[str] = []
    current = ""
    current_w = 0
    for word in text.split(" "):
        w = cell_len(word)
        if current_w == 0:
            if w > width:
                current = truncate_to(word, width)
                out.append(current)
                current = ""
                current_w = 0
                continue
            current = word
            current_w = w
        elif current_w + 1 + w <= width:
            current += " " + word
            current_w += 1 + w
        else:
            out.append(current)
            current = word
            current_w = w
    if current or not out:
        out.append(current)
    return out


def _print_bordered_text(console: Console, text: str, style: Style | None, *, wrap: bool) -> None:
    body_style = style or theme.BODY
    if not wrap:
        console.print(bordered_line(text, body_style))
        return
    inner = inner_width()
    for chunk in _wrap_cells(text, inner):
        console.print(bordered_line(chunk, body_style))


class Form:
    """Context manager for a single command form.

    Usage::

        with Form(title="version") as form:
            form.line("Consultando registros do bureau...")
            form.stamp(stamp_review("norman 0.1.0"))
    """

    def __init__(
        self,
        title: str,
        *,
        console: Console | None = None,
        show_header: bool = True,
        signature_text: str | None = None,
    ) -> None:
        self.title = title
        self.console = console or Console(highlight=False, soft_wrap=False)
        self._show_header = show_header
        self._signature_text = signature_text
        self._closed = False

    def __enter__(self) -> Self:
        print_top(self.console, self.title)
        if self._show_header:
            print_bordered_renderable(self.console, render_header())
            print_divider(self.console)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._closed:
            return
        self._print_signature()
        print_bottom(self.console)
        self._closed = True

    def line(self, text: str = "", style: Style | None = None, *, wrap: bool = True) -> None:
        _print_bordered_text(self.console, text, style, wrap=wrap)

    def divider(self) -> None:
        print_divider(self.console)

    def stamp(self, renderable: RenderableType) -> None:
        self.divider()
        print_bordered_renderable(self.console, renderable)

    async def run_pending(self, jobs: list[Job]) -> list[JobOutcome]:
        """Spawn `jobs` as background tasks and render them as a live region.

        Returns the outcomes (in registration order) once every job reaches a
        terminal state. Failures are isolated — the caller still decides how
        to carry them into the foreground stamp.
        """
        if not jobs:
            return []
        async with JobRunner() as runner:
            handles = [runner.spawn(job) for job in jobs]
            async with PendingJobsRegion(self.console, handles) as region:
                await region.wait()
        return runner.outcomes

    def _print_signature(self) -> None:
        self.divider()
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        signature = self._signature_text or get_settings().director_signature
        text = f"{signature}  ·  {timestamp}"
        inner = inner_width()
        truncated = truncate_to(text, inner)
        padded = " " * (inner - cell_len(truncated)) + truncated
        line = Text()
        line.append("║ ", style=theme.BORDER)
        line.append(padded, style=theme.SIGNATURE)
        line.append(" ║", style=theme.BORDER)
        self.console.print(line)
