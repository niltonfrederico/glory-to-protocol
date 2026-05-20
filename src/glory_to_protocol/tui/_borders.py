from __future__ import annotations

from rich.cells import cell_len
from rich.console import Console
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from glory_to_protocol.tui import theme

_SIDE_PADDING = 4


def inner_width() -> int:
    return theme.FORM_WIDTH - _SIDE_PADDING


def truncate_to(text: str, width: int) -> str:
    if cell_len(text) <= width:
        return text
    out: list[str] = []
    used = 0
    for ch in text:
        w = cell_len(ch)
        if used + w > width:
            break
        out.append(ch)
        used += w
    return "".join(out)


def print_top(console: Console, title: str) -> None:
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


def print_bottom(console: Console) -> None:
    line = "╚" + ("═" * (theme.FORM_WIDTH - 2)) + "╝"
    console.print(Text(line, style=theme.BORDER))


def print_divider(console: Console) -> None:
    line = "╠" + ("═" * (theme.FORM_WIDTH - 2)) + "╣"
    console.print(Text(line, style=theme.BORDER))


def bordered_line(text: str, style: Style = theme.BODY) -> Text:
    inner = inner_width()
    body = truncate_to(text, inner)
    padding = inner - cell_len(body)
    line = Text()
    line.append("║ ", style=theme.BORDER)
    line.append(body, style=style)
    line.append(" " * padding)
    line.append(" ║", style=theme.BORDER)
    return line


def bordered_split(left: str, right: str, right_style: Style) -> Text:
    inner = inner_width()
    left_w = cell_len(left)
    right_w = cell_len(right)
    if left_w + right_w > inner:
        left = truncate_to(left, inner - right_w)
        left_w = cell_len(left)
    padding = inner - left_w - right_w

    line = Text()
    line.append("║ ", style=theme.BORDER)
    line.append(left, style=theme.BODY)
    line.append(" " * padding)
    line.append(right, style=right_style)
    line.append(" ║", style=theme.BORDER)
    return line


def print_bordered_renderable(console: Console, renderable: RenderableType) -> None:
    inner = inner_width()
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
