import glory_to_protocol


def test_should_expose_protocol_on_package_root():
    assert glory_to_protocol.Protocol is not None


def test_should_expose_expose_decorator_on_package_root():
    assert callable(glory_to_protocol.expose)


def test_should_expose_strings_catalog_on_package_root():
    from glory_to_protocol.strings import Strings as RealStrings

    assert glory_to_protocol.Strings is RealStrings


def test_should_expose_protocol_unavailable_on_package_root():
    from glory_to_protocol.protocol import ProtocolUnavailable as Real

    assert glory_to_protocol.ProtocolUnavailable is Real


def test_should_expose_exposed_command_on_package_root():
    from glory_to_protocol.registry import ExposedCommand as Real

    assert glory_to_protocol.ExposedCommand is Real


def test_should_expose_mode_enum_on_package_root():
    from glory_to_protocol.settings import Mode as RealMode

    assert glory_to_protocol.Mode is RealMode


def test_should_expose_fallback_enum_on_package_root():
    from glory_to_protocol.settings import Fallback as RealFallback

    assert glory_to_protocol.Fallback is RealFallback


def test_should_include_all_new_symbols_in_dunder_all():
    expected = {
        "Protocol",
        "ProtocolUnavailable",
        "ExposedCommand",
        "Strings",
        "expose",
        "Mode",
        "Fallback",
    }
    assert expected.issubset(set(glory_to_protocol.__all__))


def test_should_raise_attribute_error_for_unknown_symbol():
    import pytest

    with pytest.raises(AttributeError):
        _ = glory_to_protocol.this_does_not_exist  # type: ignore[attr-defined]
