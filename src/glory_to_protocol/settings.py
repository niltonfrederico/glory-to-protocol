from functools import cache
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

    bureau_title: str = Field("БЮРО НИРВЫТЕХ · Bureau of Computational Technology")
    director_name: str = Field("Норман")
    director_signature: str = Field("Подписано: Норман, Директор НИРВЫТЕХ")

    ascii: ASCIISettings = ASCIISettings()

    model_config = SettingsConfigDict(env_prefix="PROTOCOL_")

    @model_validator(mode="after")
    def validate_logo_text_characters(self) -> Self:
        disallowed = {c for c in self.logo_text.upper() if c not in self.ascii.allowed_characters}
        if disallowed:
            raise InvalidASCIICharactersError(disallowed)
        return self


@cache
def get_settings() -> ProtocolSettings:
    return ProtocolSettings()
