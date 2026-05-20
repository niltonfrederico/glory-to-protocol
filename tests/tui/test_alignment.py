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
from tests.tui._helpers import assert_borders_aligned
from tests.tui.conftest import save_snapshot

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def test_should_render_aligned_frame_when_form_has_no_lines(snapshot_console: Console) -> None:
    with Form(title="empty", console=snapshot_console, show_header=False) as form:
        del form
    out = snapshot_console.export_text()
    save_snapshot("empty_form", out)
    assert_borders_aligned(out)


def test_should_render_header_when_form_has_title(snapshot_console: Console) -> None:
    with Form(title="version", console=snapshot_console) as form:
        form.line("Linha simples ASCII")
    out = snapshot_console.export_text()
    save_snapshot("form_with_header", out)
    assert_borders_aligned(out)


def test_should_align_borders_when_form_renders_cyrillic_lines(
    snapshot_console: Console,
) -> None:
    with Form(title="cyrillic", console=snapshot_console, show_header=False) as form:
        form.line("Норман Директор Бюро")
        form.line("Mixed: Норман / Norman · Бюро / Bureau")
        form.line("ASCII only after cyrillic")
    out = snapshot_console.export_text()
    save_snapshot("form_cyrillic", out)
    assert_borders_aligned(out)


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
    out = snapshot_console.export_text()
    save_snapshot(f"form_{name}", out)
    assert_borders_aligned(out)


@pytest.mark.parametrize("logo", [LOGO_LARGE, LOGO_SMALL])
def test_should_keep_cells_aligned_when_rendering_logo(logo: str) -> None:
    lines = logo.splitlines()
    widths = {cell_len(line) for line in lines}
    assert len(widths) == 1, f"logo lines have varying width: {widths}"


def test_should_strip_ansi_when_writing_snapshot_file(snapshot_console: Console) -> None:
    """export_text must strip ANSI; if it ever leaks, fail loudly."""
    with Form(title="ansi-check", console=snapshot_console) as form:
        form.line("colored line", style=theme.STAMP_APPROVE)
        form.stamp(stamp_approve("ok"))
    out = snapshot_console.export_text()
    save_snapshot("ansi_check", out)
    assert ANSI_RE.sub("", out) == out, "ANSI sequences leaked into export_text output"
