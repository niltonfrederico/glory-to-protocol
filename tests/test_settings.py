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
