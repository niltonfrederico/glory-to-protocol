from typing import Self

from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from glory_to_protocol.tui import _ascii
from glory_to_protocol.tui.exceptions import InvalidASCIICharactersError
from glory_to_protocol.validators.base import has_disallowed_characters

_DEFAULT_APP_NAME = "Protocol"


class ASCIISettings(BaseModel):
    allowed_symbols: dict[str, str] = {"★": ":star:", ":star:": ":star:"}
    allowed_misc: set[str] = {" "}

    allowed_alphabet: set[str] = Field(default_factory=lambda: set(_ascii.ALPHABET.keys()))

    @computed_field
    @property
    def allowed_characters(self) -> set[str]:
        return self.allowed_alphabet | set(self.allowed_symbols.keys()) | self.allowed_misc


class ProtocolSettings(BaseSettings):
    app_name: str = Field(_DEFAULT_APP_NAME)
    logo_text: str = Field(_DEFAULT_APP_NAME)
    small_logo_text: str = Field(_DEFAULT_APP_NAME)

    ascii: ASCIISettings = ASCIISettings()

    model_config = SettingsConfigDict(env_prefix="PROTOCOL_")

    @model_validator(mode="after")
    def validate_logo_text_characters(self) -> Self:
        is_valid, disallowed_chars = has_disallowed_characters(
            self.logo_text.upper(), self.ascii.allowed_characters
        )
        if not is_valid:
            raise InvalidASCIICharactersError(disallowed_chars)
        return self


settings = ProtocolSettings()
