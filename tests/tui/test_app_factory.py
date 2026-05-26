import typer

from glory_to_protocol.protocol import Protocol
from glory_to_protocol.registry import expose
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.app import ProtocolApp


def _build_typer():
    typer_app = typer.Typer()

    @typer_app.callback()
    def _root() -> None:
        pass

    @typer_app.command()
    @expose(section="data")
    def ingest(path: str) -> None:
        """Pull data."""

    return typer_app


def test_should_use_protocol_app_when_no_factory_provided(monkeypatch):
    typer_app = _build_typer()
    protocol = Protocol(typer_app=typer_app, settings=ProtocolSettings())
    captured: list[type] = []

    def fake_run(self):  # noqa: ANN001
        captured.append(type(self))
        return None

    monkeypatch.setattr("textual.app.App.run", fake_run)
    protocol._dispatch_textual()
    assert captured == [ProtocolApp]


def test_should_use_custom_factory_when_provided(monkeypatch):
    typer_app = _build_typer()

    class _MyApp(ProtocolApp):
        pass

    protocol = Protocol(
        typer_app=typer_app,
        settings=ProtocolSettings(),
        app_factory=_MyApp,
    )
    captured: list[type] = []

    def fake_run(self):  # noqa: ANN001
        captured.append(type(self))
        return None

    monkeypatch.setattr("textual.app.App.run", fake_run)
    protocol._dispatch_textual()
    assert captured == [_MyApp]


def test_should_expose_textual_symbols_from_public_module():
    import glory_to_protocol as gp

    assert gp.ProtocolApp is not None
    assert gp.PaletteScreen is not None
    assert gp.FormScreen is not None
    assert gp.HelpOverlay is not None
    assert gp.BureauTheme is not None
    assert gp.LayoutSettings is not None
    assert gp.OfficialHeader is not None
    assert gp.BindingsFooter is not None
    assert gp.ExposedCommandProvider is not None
    assert gp.LOGO_MEDIUM is not None
    assert callable(gp.logo_medium)
    assert callable(gp.render_result_stamp)
