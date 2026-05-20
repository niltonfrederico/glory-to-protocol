from __future__ import annotations

import os
import uuid
from datetime import UTC
from datetime import datetime
from functools import cache

from rich.align import Align
from rich.console import Group
from rich.console import RenderableType
from rich.text import Text

from glory_to_protocol.settings import get_settings
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.logo import logo_large


@cache
def _default_session_id() -> str:
    return uuid.uuid4().hex[:8]


def _session_id() -> str:
    explicit = os.getenv("PROTOCOL_SESSION_ID")
    if explicit:
        return explicit
    return _default_session_id()


def render_header(
    *,
    bureau_title: str | None = None,
    director: str | None = None,
) -> RenderableType:
    """Header renderable meant to be embedded inside the form borders.

    Defaults to NIRVYTEKH values from settings; pass overrides for other bureaus.
    """
    cfg = get_settings()
    bureau_title = bureau_title or cfg.bureau_title
    director = director or cfg.director_name
    logo = Text(logo_large(), style=theme.HEADER)
    title = Text(bureau_title, style=theme.CYRILLIC_ACCENT)
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    meta = Text()
    meta.append("Директор: ", style=theme.MUTED)
    meta.append(director, style=theme.BODY)
    meta.append("  ·  ", style=theme.MUTED)
    meta.append("Дата: ", style=theme.MUTED)
    meta.append(today, style=theme.BODY)
    meta.append("  ·  ", style=theme.MUTED)
    meta.append("Сессия: ", style=theme.MUTED)
    meta.append(f"#{_session_id()}", style=theme.BODY)

    rule = Text("─── ОФИЦИАЛЬНО ───", style=theme.MUTED)

    return Group(
        Align.center(logo),
        Align.center(Text("★", style=theme.CYRILLIC_ACCENT)),
        Align.center(title),
        Align.center(meta),
        Text(""),
        Align.center(rule),
    )
