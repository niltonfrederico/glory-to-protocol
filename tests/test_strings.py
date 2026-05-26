from glory_to_protocol.strings import FormStrings
from glory_to_protocol.strings import HeaderStrings
from glory_to_protocol.strings import PaletteStrings
from glory_to_protocol.strings import StampStrings
from glory_to_protocol.strings import Strings
from glory_to_protocol.strings import ViewportStrings


def test_should_expose_stamp_defaults_in_cyrillic():
    s = StampStrings()
    assert s.approved == "ОДОБРЕНО"
    assert s.rejected == "ОТКАЗАНО"
    assert s.pending == "В ОЧЕРЕДИ"


def test_should_expose_palette_placeholder_default():
    s = PaletteStrings()
    assert s.title == "ДИРЕКТИВЫ"
    assert s.placeholder == "Найти директиву…"


def test_should_expose_form_submit_default():
    assert FormStrings().submit == "ОТПРАВИТЬ"


def test_should_expose_header_motto_default():
    assert HeaderStrings().motto == "Слава ПРОТОКОЛУ"


def test_should_format_viewport_too_small_body_with_dimensions():
    body = ViewportStrings().too_small_body.format(min_w=80, min_h=24, cur_w=40, cur_h=12)
    assert "80" in body
    assert "40" in body


def test_should_compose_full_catalog_with_subgroups():
    s = Strings()
    assert isinstance(s.stamps, StampStrings)
    assert isinstance(s.palette, PaletteStrings)
    assert isinstance(s.forms, FormStrings)
    assert isinstance(s.header, HeaderStrings)
    assert isinstance(s.viewport, ViewportStrings)


def test_should_override_subgroup_when_passed_to_catalog():
    s = Strings(stamps=StampStrings(approved="APROVADO"))
    assert s.stamps.approved == "APROVADO"
    assert s.stamps.rejected == "ОТКАЗАНО"
