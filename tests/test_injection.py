from __future__ import annotations

import io

import pytest
from rich.console import Console

from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.header import _default_session_id
from glory_to_protocol.tui.header import _session_id
from glory_to_protocol.tui.header import render_header


def _render_to_string(renderable: object) -> str:
    buf = io.StringIO()
    console = Console(file=buf, width=200, force_terminal=False, highlight=False)
    console.print(renderable)
    return buf.getvalue()


def test_should_keep_stable_session_id_across_renders(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROTOCOL_SESSION_ID", raising=False)
    _default_session_id.cache_clear()
    first = _session_id()
    second = _session_id()
    assert first == second


def test_should_use_default_nirvytekh_strings_when_no_override() -> None:
    output = _render_to_string(render_header())
    assert "БЮРО НИРВЫТЕХ" in output
    assert "Норман" in output


def test_should_override_bureau_title_when_provided() -> None:
    output = _render_to_string(
        render_header(bureau_title="ПРОТОН · Proton Bureau", director="Эмма")
    )
    assert "ПРОТОН · Proton Bureau" in output
    assert "Эмма" in output


def test_should_use_default_signature_when_form_signature_not_overridden() -> None:
    buf = io.StringIO()
    console = Console(file=buf, width=200, force_terminal=False, highlight=False)
    with Form(title="t", console=console, show_header=False):
        pass
    output = buf.getvalue()
    assert "Подписано: Норман, Директор НИРВЫТЕХ" in output


def test_should_use_custom_signature_when_form_signature_overridden() -> None:
    buf = io.StringIO()
    console = Console(file=buf, width=200, force_terminal=False, highlight=False)
    with Form(
        title="t",
        console=console,
        show_header=False,
        signature_text="Подписано: Эмма, Директор ПРОТОН",
    ):
        pass
    output = buf.getvalue()
    assert "Подписано: Эмма, Директор ПРОТОН" in output
