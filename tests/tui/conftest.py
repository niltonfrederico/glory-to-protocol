from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from rich.console import Console

SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "logs" / "tui-snapshots"


@pytest.fixture(autouse=True)
def _ensure_snapshot_dir() -> Iterator[None]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture()
def snapshot_console() -> Console:
    """A recording console with a fixed width matching the form."""
    return Console(
        record=True,
        width=80,
        force_terminal=False,
        soft_wrap=False,
        highlight=False,
        legacy_windows=False,
    )


def save_snapshot(name: str, content: str) -> Path:
    path = SNAPSHOT_DIR / f"{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path
