from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from glory_to_protocol.settings import LogoSize
from glory_to_protocol.tui.identity import BureauTheme
from glory_to_protocol.tui.logo import logo_large
from glory_to_protocol.tui.logo import logo_medium
from glory_to_protocol.tui.logo import logo_small


def _render_logo(theme: BureauTheme, size: LogoSize) -> str:
    if size == "small":
        return logo_small(theme.logo_text)
    if size == "large":
        return logo_large(theme.logo_text)
    return logo_medium(theme.logo_text)


class OfficialHeader(Widget):
    DEFAULT_CSS = """
    OfficialHeader {
        height: auto;
        border: heavy $accent;
        border-title-color: $gold;
        padding: 0 1;
    }
    OfficialHeader > Horizontal {
        height: auto;
    }
    OfficialHeader .logo {
        color: $gold;
        width: auto;
        padding-right: 2;
    }
    OfficialHeader .meta {
        color: $text-color;
        width: 1fr;
        content-align: right top;
    }
    OfficialHeader .subtitle {
        color: $muted;
    }
    """

    def __init__(self, theme: BureauTheme, logo_size: LogoSize) -> None:
        super().__init__()
        self._theme = theme
        self._logo_size = logo_size
        self.border_title = theme.name

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(_render_logo(self._theme, self._logo_size), classes="logo"),
            Vertical(
                Static(self._theme.name, classes="meta"),
                Static(self._theme.subtitle, classes="subtitle"),
            ),
        )
