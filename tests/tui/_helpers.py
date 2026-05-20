from __future__ import annotations

from rich.cells import cell_len

from glory_to_protocol.tui import theme


def assert_borders_aligned(text: str, width: int = theme.FORM_WIDTH) -> None:
    """Every framed line must have the same cell width and end with the right border."""
    framed_lines = [line for line in text.splitlines() if line.startswith(("╔", "║", "╠", "╚"))]
    assert framed_lines, "no framed lines found"
    for line in framed_lines:
        assert cell_len(line) == width, f"line width {cell_len(line)} != {width}: {line!r}"
        assert line[-1] in {"╗", "║", "╣", "╝"}, f"unexpected right border: {line!r}"
