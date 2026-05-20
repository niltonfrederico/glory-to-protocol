from glory_to_protocol.settings import settings
from glory_to_protocol.tui import _ascii

_SPACE_WIDTH = 4
_SMALL_PADDING = 1
_SYMBOL_GLYPHS: dict[str, tuple[str, ...]] = {"★": _ascii.STAR, ":star:": _ascii.STAR}


def _glyph_for(char: str) -> tuple[str, ...]:
    if char == " ":
        return tuple(" " * _SPACE_WIDTH for _ in range(_ascii.GLYPH_HEIGHT))
    if char in _SYMBOL_GLYPHS:
        return _SYMBOL_GLYPHS[char]
    return _ascii.ALPHABET[char.upper()]


def _build_large(text: str) -> str:
    glyphs = [_glyph_for(char) for char in text]
    rows = ["".join(glyph[row] for glyph in glyphs) for row in range(_ascii.GLYPH_HEIGHT)]
    return "\n".join(rows)


def _build_small(text: str) -> str:
    inner_width = len(text) + 2 * _SMALL_PADDING
    border = "═" * inner_width
    pad = " " * _SMALL_PADDING
    return f"╔{border}╗\n║{pad}{text}{pad}║\n╚{border}╝"


LOGO_LARGE = _build_large(settings.logo_text)
LOGO_SMALL = _build_small(settings.small_logo_text)
