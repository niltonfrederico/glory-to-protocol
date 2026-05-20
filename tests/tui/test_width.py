import pytest

from glory_to_protocol.tui.width import cell_len
from glory_to_protocol.tui.width import pad_to
from glory_to_protocol.tui.width import truncate_to


def test_should_return_cell_count_when_cell_len_called_on_latin() -> None:
    assert cell_len("abc") == 3


@pytest.mark.parametrize(
    ("text", "width", "expected"),
    [
        ("ab", 5, "ab   "),
        ("abcde", 5, "abcde"),
        ("abcdef", 3, "abcdef"),
    ],
)
def test_should_return_padded_text_when_pad_to_called(text: str, width: int, expected: str) -> None:
    assert pad_to(text, width) == expected


@pytest.mark.parametrize(
    ("text", "width", "expected"),
    [
        ("abc", 5, "abc"),
        ("abcdef", 3, "abc"),
        ("Норман", 4, "Норм"),
    ],
)
def test_should_return_truncated_text_when_truncate_to_called(
    text: str, width: int, expected: str
) -> None:
    assert truncate_to(text, width) == expected
