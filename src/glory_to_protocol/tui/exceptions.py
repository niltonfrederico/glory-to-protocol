from collections.abc import Iterable


class ASCIIParseError(ValueError):
    """Base for all ASCII parsing errors."""


class InvalidASCIICharactersError(ASCIIParseError):
    """Raised when text contains characters outside the allowed ASCII set."""

    def __init__(self, invalid_characters: Iterable[str]) -> None:
        self.invalid_characters: tuple[str, ...] = tuple(sorted(set(invalid_characters)))
        super().__init__(f"disallowed characters: {list(self.invalid_characters)}")
