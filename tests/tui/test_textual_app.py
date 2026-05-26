import typer
from textual.widgets import Static

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.settings import LayoutSettings
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.identity import BureauTheme
from glory_to_protocol.tui.widgets.footer import BindingsFooter
from glory_to_protocol.tui.widgets.header import OfficialHeader


def _build_protocol(layout: LayoutSettings | None = None) -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    settings = ProtocolSettings(layout=layout) if layout is not None else ProtocolSettings()
    return Protocol(typer_app=typer_app, settings=settings)


async def test_should_mount_header_and_footer_when_app_runs():
    app = ProtocolApp(_build_protocol())
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        footer = app.query_one(BindingsFooter)
        assert header.border_title == "NIRVYTEKH"
        assert "quit" in str(footer.renderable).lower()


async def test_should_carry_custom_bureau_name_in_header_when_theme_overridden():
    layout = LayoutSettings(bureau=BureauTheme(name="PROTON"))
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        assert header.border_title == "PROTON"


async def test_should_expose_theme_colors_as_css_variables_when_app_runs():
    layout = LayoutSettings(bureau=BureauTheme(accent="#00ffea", gold="#abcdef"))
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        variables = app.get_css_variables()
        assert variables["accent"] == "#00ffea"
        assert variables["gold"] == "#abcdef"


async def test_should_render_small_logo_when_logo_size_small():
    layout = LayoutSettings(logo_size="small")
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        logo_text = str(header.query_one(".logo", Static).renderable)
        # Small padding (1) yields "║ NIRVYTEKH ║" tight; medium yields wide spaces.
        assert "║ NIRVYTEKH ║" in logo_text


async def test_should_render_large_logo_when_logo_size_large():
    layout = LayoutSettings(logo_size="large")
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        logo_text = str(header.query_one(".logo", Static).renderable)
        # Large logo uses block ANSI Shadow font, has multi-row glyphs with ║ characters
        assert "█" in logo_text


async def test_should_use_custom_footer_labels_when_theme_overrides_them():
    layout = LayoutSettings(bureau=BureauTheme(footer_labels={"quit": "SAIR", "help": "AJUDA"}))
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        footer = app.query_one(BindingsFooter)
        rendered = str(footer.renderable)
        assert "SAIR" in rendered
        assert "AJUDA" in rendered
