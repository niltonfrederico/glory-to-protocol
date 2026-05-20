from glory_to_protocol.tui import _ascii
from glory_to_protocol.tui.logo import _build_large
from glory_to_protocol.tui.logo import _build_small
from glory_to_protocol.tui.logo import _glyph_for


def test_should_return_space_block_when_glyph_for_space() -> None:
    glyph = _glyph_for(" ")
    assert len(glyph) == _ascii.GLYPH_HEIGHT
    assert all(row.strip() == "" for row in glyph)


def test_should_return_star_glyph_when_glyph_for_star() -> None:
    assert _glyph_for("★") is _ascii.STAR


def test_should_uppercase_lookup_when_glyph_for_lowercase_letter() -> None:
    assert _glyph_for("a") == _ascii.ALPHABET["A"]


def test_should_render_all_rows_when_build_large_runs() -> None:
    rendered = _build_large("AB")
    assert rendered.count("\n") == _ascii.GLYPH_HEIGHT - 1


def test_should_wrap_text_with_box_when_build_small_runs() -> None:
    rendered = _build_small("Hi")
    assert rendered.startswith("╔")
    assert "║ Hi ║" in rendered
    assert rendered.endswith("╝")
