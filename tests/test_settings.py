from collections.abc import Iterator

import pytest
from pydantic import ValidationError

from glory_to_protocol.settings import ASCIISettings
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.settings import configure
from glory_to_protocol.settings import get_settings
from glory_to_protocol.settings import reset_settings
from glory_to_protocol.tui.exceptions import InvalidASCIICharactersError


@pytest.fixture(autouse=True)
def _isolate_settings() -> Iterator[None]:
    reset_settings()
    yield
    reset_settings()


def test_should_compute_allowed_characters_from_three_sets() -> None:
    ascii_settings = ASCIISettings()
    assert "A" in ascii_settings.allowed_characters
    assert " " in ascii_settings.allowed_characters
    assert "★" in ascii_settings.allowed_characters


def test_should_accept_lowercase_logo_text_when_letters_in_alphabet() -> None:
    settings = ProtocolSettings(logo_text="protocol")
    assert settings.logo_text == "protocol"


def test_should_raise_when_logo_text_has_disallowed_characters() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ProtocolSettings(logo_text="proto@col!")
    cause = excinfo.value.errors()[0]["ctx"]["error"]
    assert isinstance(cause, InvalidASCIICharactersError)
    assert set(cause.invalid_characters) == {"@", "!"}


def test_should_override_singleton_when_configure_called() -> None:
    configure(app_name="MyBureau", director_name="Ada")
    assert get_settings().app_name == "MyBureau"
    assert get_settings().director_name == "Ada"


def test_should_layer_overrides_when_configure_called_twice() -> None:
    configure(app_name="MyBureau")
    configure(director_name="Ada")
    assert get_settings().app_name == "MyBureau"
    assert get_settings().director_name == "Ada"


def test_should_clear_singleton_when_reset_settings_called() -> None:
    configure(app_name="MyBureau")
    reset_settings()
    assert get_settings().app_name == "Protocol"


def test_should_default_mode_to_hybrid_when_unset():
    settings = ProtocolSettings()
    assert settings.mode == "hybrid"


def test_should_default_fallback_to_rich_when_unset():
    settings = ProtocolSettings()
    assert settings.fallback == "rich"


def test_should_load_mode_from_env_when_protocol_mode_set(monkeypatch):
    monkeypatch.setenv("PROTOCOL_MODE", "cli")
    settings = ProtocolSettings()
    assert settings.mode == "cli"


def test_should_raise_when_mode_value_not_literal():
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        ProtocolSettings.model_validate({"mode": "invalid"})


def test_should_default_palette_shortcut_to_ctrl_k_when_unset():
    settings = ProtocolSettings()
    assert settings.palette.shortcut == "ctrl+k"


def test_should_default_viewport_to_80_by_24_when_unset():
    settings = ProtocolSettings()
    assert settings.viewport.min_width == 80
    assert settings.viewport.min_height == 24


def test_should_disable_require_fullscreen_by_default():
    settings = ProtocolSettings()
    assert settings.viewport.require_fullscreen is False


def test_should_load_nested_palette_shortcut_from_env(monkeypatch):
    monkeypatch.setenv("PROTOCOL_PALETTE__SHORTCUT", "ctrl+l")
    settings = ProtocolSettings()
    assert settings.palette.shortcut == "ctrl+l"


def test_should_default_strings_to_catalog_when_unset():
    from glory_to_protocol.strings import Strings

    settings = ProtocolSettings()
    assert isinstance(settings.strings, Strings)
    assert settings.strings.stamps.approved == "ОДОБРЕНО"


def test_should_override_strings_when_explicit_catalog_passed():
    from glory_to_protocol.strings import StampStrings
    from glory_to_protocol.strings import Strings

    overridden = Strings(stamps=StampStrings(approved="APROVADO"))
    settings = ProtocolSettings(strings=overridden)
    assert settings.strings.stamps.approved == "APROVADO"


def test_should_load_nested_strings_from_env(monkeypatch):
    monkeypatch.setenv("PROTOCOL_STRINGS__PALETTE__TITLE", "COMANDOS")
    settings = ProtocolSettings()
    assert settings.strings.palette.title == "COMANDOS"


def test_should_apply_mode_override_when_configure_called():
    from glory_to_protocol.settings import Mode
    from glory_to_protocol.settings import configure
    from glory_to_protocol.settings import reset_settings

    reset_settings()
    configured = configure(mode=Mode.TUI)
    assert configured.mode is Mode.TUI
    reset_settings()


def test_should_apply_nested_strings_override_when_configure_called():
    from glory_to_protocol.settings import configure
    from glory_to_protocol.settings import reset_settings
    from glory_to_protocol.strings import StampStrings
    from glory_to_protocol.strings import Strings

    reset_settings()
    configured = configure(
        strings=Strings(stamps=StampStrings(approved="APROVADO")),
    )
    assert configured.strings.stamps.approved == "APROVADO"
    reset_settings()


def test_should_preserve_other_fields_when_configure_overrides_one():
    from glory_to_protocol.settings import Fallback
    from glory_to_protocol.settings import Mode
    from glory_to_protocol.settings import configure
    from glory_to_protocol.settings import reset_settings

    reset_settings()
    configured = configure(mode=Mode.TUI)
    assert configured.mode is Mode.TUI
    assert configured.fallback is Fallback.RICH
    reset_settings()


def test_should_default_layout_to_nirvytekh_when_unset():
    settings = ProtocolSettings()
    assert settings.layout.bureau.name == "NIRVYTEKH"
    assert settings.layout.logo_size == "medium"
    assert settings.layout.show_result_stamp is True
    assert settings.layout.keybinds["quit"] == "q"


def test_should_load_layout_bureau_field_from_env(monkeypatch):
    monkeypatch.setenv("PROTOCOL_LAYOUT__BUREAU__ACCENT", "#00ffea")
    settings = ProtocolSettings()
    assert settings.layout.bureau.accent == "#00ffea"


def test_should_load_layout_logo_size_from_env(monkeypatch):
    monkeypatch.setenv("PROTOCOL_LAYOUT__LOGO_SIZE", "large")
    settings = ProtocolSettings()
    assert settings.layout.logo_size == "large"


def test_should_override_layout_when_configure_called():
    from glory_to_protocol.settings import LayoutSettings
    from glory_to_protocol.settings import configure
    from glory_to_protocol.settings import reset_settings
    from glory_to_protocol.tui.identity import BureauTheme

    reset_settings()
    configured = configure(layout=LayoutSettings(bureau=BureauTheme(name="PROTON")))
    assert configured.layout.bureau.name == "PROTON"
    reset_settings()
