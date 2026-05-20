from __future__ import annotations

import re
from collections.abc import Callable

import pytest
from rich.console import Console
from rich.console import RenderableType

from glory_to_protocol.tui import Form
from glory_to_protocol.tui import stamp_approve
from glory_to_protocol.tui import stamp_order
from glory_to_protocol.tui import stamp_reject
from glory_to_protocol.tui import stamp_review
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.logo import LOGO_LARGE
from glory_to_protocol.tui.logo import LOGO_SMALL
from glory_to_protocol.tui.width import cell_len
from tests.tui.conftest import save_snapshot

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def _render(console: Console) -> str:
    return console.export_text()


def _assert_borders_aligned(text: str, width: int = theme.FORM_WIDTH) -> None:
    """Every framed line must have the same cell width and end with the right border."""
    framed_lines = [line for line in text.splitlines() if line.startswith(("╔", "║", "╠", "╚"))]
    assert framed_lines, "no framed lines found"
    for line in framed_lines:
        assert cell_len(line) == width, f"line width {cell_len(line)} != {width}: {line!r}"
        assert line[-1] in {"╗", "║", "╣", "╝"}, f"unexpected right border: {line!r}"


def test_should_render_aligned_frame_when_form_has_no_lines(snapshot_console: Console) -> None:
    with Form(title="empty", console=snapshot_console, show_header=False) as form:
        del form
    out = _render(snapshot_console)
    save_snapshot("empty_form", out)
    _assert_borders_aligned(out)


def test_should_render_header_when_form_has_title(snapshot_console: Console) -> None:
    with Form(title="version", console=snapshot_console) as form:
        form.line("Linha simples ASCII")
    out = _render(snapshot_console)
    save_snapshot("form_with_header", out)
    _assert_borders_aligned(out)


def test_should_align_borders_when_form_renders_cyrillic_lines(
    snapshot_console: Console,
) -> None:
    with Form(title="cyrillic", console=snapshot_console, show_header=False) as form:
        form.line("Норман Директор Бюро")
        form.line("Mixed: Норман / Norman · Бюро / Bureau")
        form.line("ASCII only after cyrillic")
    out = _render(snapshot_console)
    save_snapshot("form_cyrillic", out)
    _assert_borders_aligned(out)


@pytest.mark.parametrize(
    ("name", "factory"),
    [
        ("stamp_approve", lambda: stamp_approve("Task created", "id=42")),
        ("stamp_reject", lambda: stamp_reject("Validation failed", "missing title")),
        ("stamp_order", lambda: stamp_order("Execute migration", "Gensek directive")),
        ("stamp_review", lambda: stamp_review("Status report", "all green")),
    ],
)
def test_should_render_aligned_frame_when_form_includes_each_stamp_variant(
    snapshot_console: Console,
    name: str,
    factory: Callable[[], RenderableType],
) -> None:
    with Form(title=name, console=snapshot_console, show_header=False) as form:
        form.line("Pre-stamp line")
        form.stamp(factory())
    out = _render(snapshot_console)
    save_snapshot(f"form_{name}", out)
    _assert_borders_aligned(out)


def test_should_keep_cells_aligned_when_rendering_large_logo() -> None:
    lines = LOGO_LARGE.splitlines()
    widths = {cell_len(line) for line in lines}
    assert len(widths) == 1, f"logo lines have varying width: {widths}"


def test_should_keep_cells_aligned_when_rendering_small_logo() -> None:
    lines = LOGO_SMALL.splitlines()
    widths = {cell_len(line) for line in lines}
    assert len(widths) == 1, f"small logo lines have varying width: {widths}"


def test_should_strip_ansi_when_writing_snapshot_file(snapshot_console: Console) -> None:
    """export_text must strip ANSI; if it ever leaks, fail loudly."""
    with Form(title="ansi-check", console=snapshot_console) as form:
        form.line("colored line", style=theme.STAMP_APPROVE)
        form.stamp(stamp_approve("ok"))
    out = _render(snapshot_console)
    save_snapshot("ansi_check", out)
    assert _strip_ansi(out) == out, "ANSI sequences leaked into export_text output"
