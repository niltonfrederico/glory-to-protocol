from functools import cache

from glory_to_protocol.settings import get_settings
from glory_to_protocol.tui import _ascii

_SPACE_WIDTH = 4
_SMALL_PADDING = 1
_MEDIUM_PADDING = 5
_SYMBOL_GLYPHS: dict[str, tuple[str, ...]] = {"★": _ascii.STAR, ":star:": _ascii.STAR}


def _glyph_for(char: str) -> tuple[str, ...]:
    if char == " ":
        return tuple(" " * _SPACE_WIDTH for _ in range(_ascii.GLYPH_HEIGHT))
    if char in _SYMBOL_GLYPHS:
        return _SYMBOL_GLYPHS[char]
    return _ascii.ALPHABET[char.upper()]


def _bordered_logo(text: str, padding: int) -> str:
    inner_width = len(text) + 2 * padding
    border = "═" * inner_width
    pad = " " * padding
    return f"╔{border}╗\n║{pad}{text}{pad}║\n╚{border}╝"


@cache
def logo_large(text: str | None = None) -> str:
    if text is None:
        text = get_settings().logo_text
    glyphs = [_glyph_for(char) for char in text]
    rows = ["".join(glyph[row] for glyph in glyphs) for row in range(_ascii.GLYPH_HEIGHT)]
    return "\n".join(rows)


@cache
def logo_medium(text: str | None = None) -> str:
    if text is None:
        text = get_settings().small_logo_text
    return _bordered_logo(text, _MEDIUM_PADDING)


@cache
def logo_small(text: str | None = None) -> str:
    if text is None:
        text = get_settings().small_logo_text
    return _bordered_logo(text, _SMALL_PADDING)


def __getattr__(name: str) -> str:
    if name == "LOGO_LARGE":
        return logo_large()
    if name == "LOGO_MEDIUM":
        return logo_medium()
    if name == "LOGO_SMALL":
        return logo_small()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
