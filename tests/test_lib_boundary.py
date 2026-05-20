from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_IMPORT_PROBE = Path(__file__).parent / "fixtures" / "import_probe.py"


def test_should_not_import_tui_when_importing_jobs() -> None:
    """Run the probe in a fresh interpreter — pytest's session has already
    imported tui/settings by the time this test runs, so sys.modules here is
    not authoritative. The subprocess gives us a clean import state.
    """
    result = subprocess.run(
        [sys.executable, str(_IMPORT_PROBE)], capture_output=True, text=True, check=True
    )
    tui_flag, settings_flag = result.stdout.strip().split()
    assert tui_flag == "0", "importing glory_to_protocol.jobs pulled in tui"
    assert settings_flag == "0", "importing glory_to_protocol.jobs parsed settings"


def test_should_expose_legacy_logo_constants_via_module_getattr() -> None:
    from glory_to_protocol.tui import logo

    assert isinstance(logo.LOGO_LARGE, str)
    assert isinstance(logo.LOGO_SMALL, str)
    assert "╔" in logo.LOGO_SMALL


def test_should_cache_settings_singleton_across_calls() -> None:
    from glory_to_protocol.settings import get_settings

    assert get_settings() is get_settings()


def test_should_resolve_public_attributes_lazily_via_package_getattr() -> None:
    import glory_to_protocol as gtp

    for name in gtp.__all__:
        assert getattr(gtp, name) is not None


def test_should_raise_attribute_error_for_unknown_package_attribute() -> None:
    import pytest

    import glory_to_protocol as gtp

    with pytest.raises(AttributeError):
        _ = gtp.does_not_exist  # type: ignore[attr-defined]


def test_should_raise_attribute_error_for_unknown_tui_attribute() -> None:
    import pytest

    from glory_to_protocol import tui

    with pytest.raises(AttributeError):
        _ = tui.does_not_exist  # type: ignore[attr-defined]


def test_should_raise_attribute_error_for_unknown_logo_attribute() -> None:
    import pytest

    from glory_to_protocol.tui import logo

    with pytest.raises(AttributeError):
        _ = logo.NOT_A_LOGO  # type: ignore[attr-defined]
