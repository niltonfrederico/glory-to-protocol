from dataclasses import dataclass
from datetime import UTC
from datetime import datetime

from rich.console import Group
from rich.style import Style
from rich.table import Table
from rich.text import Text

from glory_to_protocol.tui import theme
from glory_to_protocol.tui.logo import logo_small


@dataclass(frozen=True)
class StampKind:
    label_ru: str
    label_en: str
    style: Style


APPROVE = StampKind("ОДОБРЕНО", "APPROVED", theme.STAMP_APPROVE)
REJECT = StampKind("ОТКАЗАНО", "REJECTED", theme.STAMP_REJECT)
ORDER = StampKind("ПРИКАЗ", "DIRECT ORDER", theme.STAMP_ORDER)
REVIEW = StampKind("К СВЕДЕНИЮ", "FOR REVIEW", theme.STAMP_REVIEW)


def _stamp(kind: StampKind, label: str, detail: str) -> Table:
    logo = Text(logo_small(), style=kind.style)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    head = Text()
    head.append(f"{kind.label_ru} ", style=kind.style)
    head.append(f"/ {kind.label_en}", style=theme.MUTED)

    body = Text(label, style=theme.BODY)
    if detail:
        body.append(f"  ·  {detail}", style=theme.MUTED)

    foot = Text(timestamp, style=theme.MUTED)

    right = Group(head, body, foot)

    table = Table.grid(padding=(0, 2))
    table.add_column(no_wrap=True)
    table.add_column()
    table.add_row(logo, right)
    return table


def stamp_approve(label: str, detail: str = "") -> Table:
    return _stamp(APPROVE, label, detail)


def stamp_reject(label: str, detail: str = "") -> Table:
    return _stamp(REJECT, label, detail)


def stamp_order(label: str, detail: str = "") -> Table:
    return _stamp(ORDER, label, detail)


def stamp_review(label: str, detail: str = "") -> Table:
    return _stamp(REVIEW, label, detail)
