from __future__ import annotations

from rich.console import Console

from glory_to_protocol.tui import Form


def test_should_emit_immediately_when_form_line_is_added() -> None:
    """Each Form.line() call should produce output before the next is invoked."""
    console = Console(record=True, width=80, force_terminal=False, highlight=False)
    with Form(title="stream", console=console, show_header=False) as form:
        form.line("first")
        mid = console.export_text(clear=False)
        assert "first" in mid, "line() did not flush immediately"
        form.line("second")
    end = console.export_text(clear=False)
    assert "first" in end and "second" in end
