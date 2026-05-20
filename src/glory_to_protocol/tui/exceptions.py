from __future__ import annotations


class InvalidASCIICharactersError(ValueError):
    """Raised when text contains characters outside the allowed ASCII set."""

    def __init__(self, invalid_characters: set[str]) -> None:
        self.invalid_characters: tuple[str, ...] = tuple(sorted(invalid_characters))
        super().__init__(f"disallowed characters: {list(self.invalid_characters)}")
