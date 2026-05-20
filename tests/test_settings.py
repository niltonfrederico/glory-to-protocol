import pytest
from pydantic import ValidationError

from glory_to_protocol.settings import ASCIISettings
from glory_to_protocol.settings import ProtocolSettings
from glory_to_protocol.tui.exceptions import InvalidASCIICharactersError


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
