import asyncio
import io

from rich.console import Console

from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.forms import _print_top
from glory_to_protocol.tui.forms import _wrap_cells


def _capture_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, width=200, force_terminal=False, highlight=False), buf


def test_should_truncate_title_when_print_top_title_longer_than_width() -> None:
    console, buf = _capture_console()
    long_title = "x" * (theme.FORM_WIDTH * 2)
    _print_top(console, long_title)
    output = buf.getvalue()
    assert "╔" in output and "╗" in output


def test_should_emit_single_chunk_when_wrap_cells_empty() -> None:
    assert _wrap_cells("", 10) == [""]


def test_should_truncate_word_when_wrap_cells_word_exceeds_width() -> None:
    chunks = _wrap_cells("abcdefghij short", 4)
    assert chunks[0] == "abcd"


def test_should_push_current_when_wrap_cells_overflows_line() -> None:
    chunks = _wrap_cells("alpha beta gamma", 6)
    assert "alpha" in chunks[0]
    assert chunks[1].startswith("beta")


def test_should_noop_on_second_exit_when_form_already_closed() -> None:
    console, buf = _capture_console()
    form = Form(title="t", console=console, show_header=False)
    with form:
        form.line("hello")
    before = buf.getvalue()
    form.__exit__(None, None, None)
    assert buf.getvalue() == before


def test_should_return_empty_list_when_run_pending_called_with_no_jobs() -> None:
    console, _buf = _capture_console()
    with Form(title="t", console=console, show_header=False) as form:
        outcomes = asyncio.run(form.run_pending([]))
    assert outcomes == []
