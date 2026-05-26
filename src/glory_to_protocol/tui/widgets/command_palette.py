from __future__ import annotations

from textual.command import CommandPalette
from textual.containers import Vertical

DIRECTIVE_PROMPT = "Найти директиву…"
DIRECTIVE_TITLE = "ДИРЕКТИВА · search"
DIRECTIVE_SUBTITLE = "[ENTER] open  ·  [ESC] cancel"


class ProtocolCommandPalette(CommandPalette):
    DEFAULT_CSS = """
    ProtocolCommandPalette {
        background: $bg 80%;
    }
    ProtocolCommandPalette > Vertical#--container {
        margin-top: 4;
        width: 80%;
        max-width: 100;
        background: $bg;
        border: heavy $accent;
        border-title-color: $gold;
        border-title-style: bold;
        border-subtitle-color: $muted;
    }
    ProtocolCommandPalette SearchIcon {
        display: none;
    }
    ProtocolCommandPalette #--input {
        background: $bg;
        border: none;
        border-bottom: heavy $border;
        padding: 0 1;
    }
    ProtocolCommandPalette CommandInput {
        background: $bg;
        color: $text-color;
        border: none;
    }
    ProtocolCommandPalette CommandList {
        background: $bg;
        color: $text-color;
        border: none;
    }
    ProtocolCommandPalette > .command-palette--highlight {
        color: $gold;
        text-style: bold;
    }
    ProtocolCommandPalette > .command-palette--help-text {
        color: $muted;
    }
    """

    def __init__(self) -> None:
        super().__init__(placeholder=DIRECTIVE_PROMPT, id="--command-palette")

    def on_mount(self) -> None:
        container = self.query_one("#--container", Vertical)
        container.border_title = DIRECTIVE_TITLE
        container.border_subtitle = DIRECTIVE_SUBTITLE
