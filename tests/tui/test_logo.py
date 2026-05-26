from glory_to_protocol.tui import _ascii
from glory_to_protocol.tui.logo import _glyph_for
from glory_to_protocol.tui.logo import logo_large
from glory_to_protocol.tui.logo import logo_medium
from glory_to_protocol.tui.logo import logo_small


def test_should_return_space_block_when_glyph_for_space() -> None:
    glyph = _glyph_for(" ")
    assert len(glyph) == _ascii.GLYPH_HEIGHT
    assert all(row.strip() == "" for row in glyph)


def test_should_return_star_glyph_when_glyph_for_star() -> None:
    assert _glyph_for("★") is _ascii.STAR


def test_should_uppercase_lookup_when_glyph_for_lowercase_letter() -> None:
    assert _glyph_for("a") == _ascii.ALPHABET["A"]


def test_should_render_all_rows_when_logo_large_runs() -> None:
    rendered = logo_large("AB")
    assert rendered.count("\n") == _ascii.GLYPH_HEIGHT - 1


def test_should_wrap_text_with_box_when_logo_small_runs() -> None:
    rendered = logo_small("Hi")
    assert rendered.startswith("╔")
    assert "║ Hi ║" in rendered
    assert rendered.endswith("╝")


def test_should_wrap_text_with_wide_padding_when_logo_medium_runs() -> None:
    rendered = logo_medium("Hi")
    assert rendered.startswith("╔")
    assert "║     Hi     ║" in rendered
    assert rendered.endswith("╝")


def test_should_use_small_logo_text_setting_when_logo_medium_called_without_arg() -> None:
    from glory_to_protocol.settings import reset_settings

    reset_settings()
    rendered = logo_medium()
    assert "Protocol" in rendered
    reset_settings()


def test_should_expose_module_level_constants_via_getattr() -> None:
    import glory_to_protocol.tui.logo as logo_module
    from glory_to_protocol.settings import reset_settings

    reset_settings()
    # LOGO_LARGE renders block-shadow font; raw text is not literal letters.
    assert "█" in logo_module.LOGO_LARGE
    assert "Protocol" in logo_module.LOGO_MEDIUM
    assert "Protocol" in logo_module.LOGO_SMALL


def test_should_raise_attribute_error_when_unknown_module_attr() -> None:
    import pytest

    import glory_to_protocol.tui.logo as logo_module

    with pytest.raises(AttributeError):
        _ = logo_module.LOGO_GIANT
