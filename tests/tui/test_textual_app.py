import typer
from textual.widgets import Static

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import LayoutSettings
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp
from glory_to_protocol.tui.identity import BureauTheme
from glory_to_protocol.tui.screens.palette import PaletteScreen
from glory_to_protocol.tui.widgets.footer import BindingsFooter
from glory_to_protocol.tui.widgets.header import OfficialHeader


def _build_protocol(
    layout: LayoutSettings | None = None,
    app_name: str | None = None,
) -> Protocol:
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    settings = ProtocolSettings()
    if layout is not None:
        settings = settings.model_copy(update={"layout": layout})
    if app_name is not None:
        settings = settings.model_copy(update={"app_name": app_name})
    return Protocol(typer_app=typer_app, settings=settings)


async def test_should_mount_header_and_footer_when_app_runs():
    app = ProtocolApp(_build_protocol())
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        footer = app.query_one(BindingsFooter)
        assert header.border_title == "Protocol · Palette"
        assert "quit" in str(footer.content).lower()


async def test_should_carry_custom_app_name_in_header_when_app_name_overridden():
    app = ProtocolApp(_build_protocol(app_name="Proton"))
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        assert header.border_title == "Proton · Palette"


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
        logo_text = str(header.query_one(".logo", Static).content)
        # Small/medium render bare text inside the header (the heavy outer
        # border already frames the logo — no inner ASCII box).
        assert logo_text == "NIRVYTEKH"


async def test_should_render_large_logo_when_logo_size_large():
    layout = LayoutSettings(logo_size="large")
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        logo_text = str(header.query_one(".logo", Static).content)
        # Large logo uses block ANSI Shadow font, has multi-row glyphs with ║ characters
        assert "█" in logo_text


async def test_should_use_custom_footer_labels_when_theme_overrides_them():
    layout = LayoutSettings(bureau=BureauTheme(footer_labels={"quit": "SAIR", "help": "AJUDA"}))
    app = ProtocolApp(_build_protocol(layout=layout))
    async with app.run_test() as pilot:
        await pilot.pause()
        footer = app.query_one(BindingsFooter)
        rendered = str(footer.content)
        assert "SAIR" in rendered
        assert "AJUDA" in rendered


async def test_should_fit_body_within_terminal_when_app_runs():
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    for index in range(20):

        @typer_app.command(name=f"cmd-{index}")
        @expose(section="data")
        def _cmd(name: str = "", flag: bool = False) -> None:
            """Stress row to overflow the palette."""

    protocol = Protocol(typer_app=typer_app, settings=ProtocolSettings())
    width, height = 100, 30
    app = ProtocolApp(protocol)
    async with app.run_test(size=(width, height)) as pilot:
        await pilot.pause()
        header = app.query_one(OfficialHeader)
        footer = app.query_one(BindingsFooter)
        palette = app.query_one(PaletteScreen)
        assert header.region.y >= 0
        assert footer.region.y + footer.region.height <= height
        assert palette.region.y + palette.region.height <= footer.region.y
        assert palette.region.x + palette.region.width <= width
