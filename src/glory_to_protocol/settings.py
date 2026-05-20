from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from glory_to_protocol.tui import _ascii
from glory_to_protocol.tui.exceptions import InvalidASCIICharactersError

_DEFAULT_APP_NAME = "Protocol"


class ASCIISettings(BaseModel):
    allowed_symbols: set[str] = Field(default_factory=lambda: {"★", ":star:"})
    allowed_misc: set[str] = Field(default_factory=lambda: {" "})

    allowed_alphabet: set[str] = Field(default_factory=lambda: set(_ascii.ALPHABET.keys()))

    @computed_field
    @property
    def allowed_characters(self) -> set[str]:
        return self.allowed_alphabet | self.allowed_symbols | self.allowed_misc


class ProtocolSettings(BaseSettings):
    app_name: str = Field(_DEFAULT_APP_NAME)
    logo_text: str = Field(_DEFAULT_APP_NAME)
    small_logo_text: str = Field(_DEFAULT_APP_NAME)

    bureau_title: str = Field("БЮРО NIRVYTEKH · Bureau of Computational Technology")
    director_name: str = Field("Норман")
    director_signature: str = Field("Подписано: Норман, Директор NIRVYTEKH")

    ascii: ASCIISettings = ASCIISettings()

    model_config = SettingsConfigDict(env_prefix="PROTOCOL_")

    @model_validator(mode="after")
    def validate_logo_text_characters(self) -> Self:
        disallowed = {c for c in self.logo_text.upper() if c not in self.ascii.allowed_characters}
        if disallowed:
            raise InvalidASCIICharactersError(disallowed)
        return self


_settings: ProtocolSettings | None = None


def get_settings() -> ProtocolSettings:
    global _settings
    if _settings is None:
        _settings = ProtocolSettings()
    return _settings


def _invalidate_derived_caches() -> None:
    # Late import: logo depends on this module.
    from glory_to_protocol.tui.logo import logo_large
    from glory_to_protocol.tui.logo import logo_small

    logo_large.cache_clear()
    logo_small.cache_clear()


def configure(**overrides: Any) -> ProtocolSettings:
    """Override settings at coupling time (e.g., when wiring into a Typer app).

    Layers on top of the current settings: unspecified fields keep their value.
    Returns the new active settings.
    """
    global _settings
    base = (_settings or ProtocolSettings()).model_dump()
    base.update(overrides)
    _settings = ProtocolSettings(**base)
    _invalidate_derived_caches()
    return _settings


def reset_settings() -> None:
    """Clear the singleton — primarily for test isolation."""
    global _settings
    _settings = None
    _invalidate_derived_caches()
