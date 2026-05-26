from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static

from glory_to_protocol.settings import LogoSize
from glory_to_protocol.tui.identity import BureauTheme
from glory_to_protocol.tui.logo import logo_large

MetaCallback = Callable[[], str]

OKO_MOTTO = "Мы наблюдаем"


def default_meta_callback() -> str:
    return OKO_MOTTO


def _render_logo(theme: BureauTheme, size: LogoSize) -> str:
    if size == "large":
        return logo_large(theme.logo_text)
    return theme.logo_text


class OfficialHeader(Widget):
    DEFAULT_CSS = """
    OfficialHeader {
        height: auto;
        background: $bg;
        border: heavy $accent;
        border-title-color: $gold;
        padding: 0 1;
    }
    OfficialHeader > Horizontal {
        height: auto;
        background: $bg;
    }
    OfficialHeader .logo {
        color: $gold;
        background: $bg;
        width: auto;
        text-style: bold;
        padding-right: 2;
    }
    OfficialHeader .subtitle {
        color: $muted;
        background: $bg;
        width: auto;
    }
    OfficialHeader .meta {
        color: $text-color;
        background: $bg;
        width: 1fr;
        content-align: right top;
    }
    """

    def __init__(
        self,
        theme: BureauTheme,
        logo_size: LogoSize,
        app_name: str,
        page: str,
        meta_callback: MetaCallback | None = None,
    ) -> None:
        super().__init__()
        self._theme = theme
        self._logo_size = logo_size
        self._app_name = app_name
        self._meta_callback = meta_callback or default_meta_callback
        self.border_title = self._format_title(page)

    def _format_title(self, page: str) -> str:
        return f"{self._app_name} · {page}"

    def set_page(self, page: str) -> None:
        self.border_title = self._format_title(page)
        self.refresh_meta()

    def refresh_meta(self) -> None:
        self.query_one(".meta", Static).update(self._meta_callback())

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(_render_logo(self._theme, self._logo_size), classes="logo"),
            Static(self._theme.subtitle, classes="subtitle"),
            Static(self._meta_callback(), classes="meta"),
        )
