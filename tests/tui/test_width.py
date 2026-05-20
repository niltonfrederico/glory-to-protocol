from glory_to_protocol.tui.width import cell_len
from glory_to_protocol.tui.width import pad_to
from glory_to_protocol.tui.width import truncate_to


def test_should_return_cell_count_when_cell_len_called_on_latin() -> None:
    assert cell_len("abc") == 3


def test_should_pad_with_spaces_when_text_shorter_than_width() -> None:
    assert pad_to("ab", 5) == "ab   "


def test_should_return_text_unchanged_when_text_already_at_width() -> None:
    assert pad_to("abcde", 5) == "abcde"


def test_should_return_text_unchanged_when_text_exceeds_width() -> None:
    assert pad_to("abcdef", 3) == "abcdef"


def test_should_return_text_unchanged_when_truncate_fits() -> None:
    assert truncate_to("abc", 5) == "abc"


def test_should_truncate_to_width_when_truncate_text_too_long() -> None:
    assert truncate_to("abcdef", 3) == "abc"


def test_should_truncate_cyrillic_when_truncate_text_too_long() -> None:
    assert truncate_to("Норман", 4) == "Норм"
