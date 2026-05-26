import pytest
from pydantic import ValidationError

from glory_to_protocol.tui.identity import DEFAULT_FOOTER_LABELS
from glory_to_protocol.tui.identity import DEFAULT_STATUS_STRINGS
from glory_to_protocol.tui.identity import BureauTheme


def test_should_default_to_nirvytekh_when_no_overrides():
    theme = BureauTheme()
    assert theme.name == "NIRVYTEKH"
    assert theme.logo_text == "NIRVYTEKH"
    assert theme.accent == "#ffd84d"
    assert theme.gold == "#ffe066"
    assert theme.bg == "#0e0a05"
    assert theme.directive_prefix == "ДИРЕКТИВА №"


def test_should_carry_default_status_and_footer_strings():
    theme = BureauTheme()
    assert theme.status_strings == DEFAULT_STATUS_STRINGS
    assert theme.footer_labels == DEFAULT_FOOTER_LABELS
    assert theme.status_strings["ready"] == "Готов"
    assert theme.footer_labels["quit"] == "quit"


def test_should_accept_overrides_when_kwargs_passed():
    theme = BureauTheme(name="PROTON", accent="#00ffea")
    assert theme.name == "PROTON"
    assert theme.accent == "#00ffea"
    assert theme.gold == "#ffe066"


def test_should_reject_mutation_when_frozen():
    theme = BureauTheme()
    with pytest.raises(ValidationError):
        theme.name = "PROTON"


def test_should_override_status_strings_when_provided():
    theme = BureauTheme(status_strings={"ready": "Ready", "working": "Working"})
    assert theme.status_strings["ready"] == "Ready"
