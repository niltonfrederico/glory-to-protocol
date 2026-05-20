from __future__ import annotations

import os
import uuid
from datetime import datetime

from rich.align import Align
from rich.console import Group
from rich.console import RenderableType
from rich.text import Text

from glory_to_protocol.tui import theme
from glory_to_protocol.tui.logo import LOGO_LARGE


def _session_id() -> str:
    explicit = os.getenv("NORMAN_SESSION_ID")
    if explicit:
        return explicit
    return uuid.uuid4().hex[:8]


def render_header() -> RenderableType:
    """Header renderable meant to be embedded inside the form borders."""
    logo = Text(LOGO_LARGE, style=theme.HEADER)
    title = Text(
        "БЮРО НИРВЫТЕХ · Bureau of Computational Technology",
        style=theme.CYRILLIC_ACCENT,
    )
    today = datetime.now().strftime("%Y-%m-%d")
    meta = Text()
    meta.append("Директор: ", style=theme.MUTED)
    meta.append("Норман", style=theme.BODY)
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
