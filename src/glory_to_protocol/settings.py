from typing import Annotated
from typing import Self

from pydantic import AfterValidator
from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic import model_validator
from pydantic_settings import BaseSettings

from src.glory_to_protocol.tui import _ascii
from src.glory_to_protocol.validations import validate_allowed_characters

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

    ascii: ASCIISettings = ASCIISettings()

    class Config:
        env_prefix = "PROTOCOL_"

    @model_validator(mode="after")
    def validate_logo_text_characters(self) -> "Self":
        """
        Validates that all characters in `logo_text` are present in the `allowed_characters`
        defined by the `ASCIISettings`.
        """
        validate_allowed_characters(self.logo_text, self.ascii.allowed_characters)
        return self
