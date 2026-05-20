from __future__ import annotations

from types import TracebackType
from typing import Self

from rich.console import Console
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.header import render_header
from glory_to_protocol.tui.jobs import PendingJobsRegion
from glory_to_protocol.tui.width import cell_len
from glory_to_protocol.tui.width import truncate_to

# Total form width includes the side borders.
# Inner width = FORM_WIDTH - len("║ ") - len(" ║") = FORM_WIDTH - 4
_SIDE_PADDING = 4


def _inner_width() -> int:
    return theme.FORM_WIDTH - _SIDE_PADDING


def _print_top(console: Console, title: str) -> None:
    width = theme.FORM_WIDTH
    title_chunk = f" {title} " if title else ""
    fill = width - 2 - cell_len(title_chunk) - 2
    fill = max(fill, 0)
    line = "╔══" + title_chunk + ("═" * fill) + "╗"
    if cell_len(line) > width:
        title_chunk = truncate_to(title_chunk, width - 6)
        fill = width - 2 - cell_len(title_chunk) - 2
        line = "╔══" + title_chunk + ("═" * fill) + "╗"
    console.print(Text(line, style=theme.BORDER))


def _print_bottom(console: Console) -> None:
    line = "╚" + ("═" * (theme.FORM_WIDTH - 2)) + "╝"
    console.print(Text(line, style=theme.BORDER))


def _print_divider(console: Console) -> None:
    line = "╠" + ("═" * (theme.FORM_WIDTH - 2)) + "╣"
    console.print(Text(line, style=theme.BORDER))


def _print_bordered_text(console: Console, text: str, style: Style | None) -> None:
    inner = _inner_width()
    body_style = style or theme.BODY
    for chunk in _wrap_cells(text, inner):
        padded = chunk + " " * (inner - cell_len(chunk))
        line = Text()
        line.append("║ ", style=theme.BORDER)
        line.append(padded, style=body_style)
        line.append(" ║", style=theme.BORDER)
        console.print(line)


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


def _print_bordered_renderable(console: Console, renderable: RenderableType) -> None:
    inner = _inner_width()
    options = console.options.update(width=inner)
    lines = console.render_lines(renderable, options, pad=True)
    for segments in lines:
        text = Text()
        text.append("║ ", style=theme.BORDER)
        for seg in segments:
            if seg.text:
                text.append(seg.text, style=seg.style)
        text.append(" ║", style=theme.BORDER)
        console.print(text)


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
    ) -> None:
        self.title = title
        self.console = console or Console(highlight=False, soft_wrap=False)
        self._show_header = show_header
        self._closed = False

    def __enter__(self) -> Self:
        _print_top(self.console, self.title)
        if self._show_header:
            _print_bordered_renderable(self.console, render_header())
            _print_divider(self.console)
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
        _print_bottom(self.console)
        self._closed = True

    def line(self, text: str = "", style: Style | None = None) -> None:
        _print_bordered_text(self.console, text, style)

    def divider(self) -> None:
        _print_divider(self.console)

    def stamp(self, renderable: RenderableType) -> None:
        self.divider()
        _print_bordered_renderable(self.console, renderable)

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
        signature = Text()
        signature.append("Подписано: ", style=theme.MUTED)
        signature.append("Норман", style=theme.BODY)
        signature.append(", Директор НИРВЫТЕХ", style=theme.SIGNATURE)
        _print_bordered_text(self.console, signature.plain, theme.SIGNATURE)
