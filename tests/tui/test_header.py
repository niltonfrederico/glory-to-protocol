import pytest

from glory_to_protocol.tui.header import _session_id
from glory_to_protocol.tui.header import render_header


def test_should_return_env_value_when_session_id_env_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROTOCOL_SESSION_ID", "deadbeef")
    assert _session_id() == "deadbeef"


def test_should_return_eight_char_hex_when_session_id_env_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PROTOCOL_SESSION_ID", raising=False)
    assert len(_session_id()) == 8


def test_should_return_renderable_group_when_render_header_called() -> None:
    assert render_header() is not None
