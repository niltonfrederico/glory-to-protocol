from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from glory_to_protocol.settings import ProtocolSettings
    from glory_to_protocol.settings import configure
    from glory_to_protocol.settings import get_settings
    from glory_to_protocol.settings import reset_settings
    from glory_to_protocol.tui import Form
    from glory_to_protocol.tui import render_header
    from glory_to_protocol.tui import stamp_approve
    from glory_to_protocol.tui import stamp_order
    from glory_to_protocol.tui import stamp_reject
    from glory_to_protocol.tui import stamp_review
    from glory_to_protocol.tui import theme
    from glory_to_protocol.tui.logo import logo_large
    from glory_to_protocol.tui.logo import logo_small
    from glory_to_protocol.typer import ProtocolTyper
    from glory_to_protocol.typer import ProtocolTyperCommand
    from glory_to_protocol.typer import ProtocolTyperGroup
    from glory_to_protocol.typer import make_app

__all__ = [
    "LOGO_LARGE",
    "LOGO_SMALL",
    "Form",
    "ProtocolSettings",
    "ProtocolTyper",
    "ProtocolTyperCommand",
    "ProtocolTyperGroup",
    "configure",
    "get_settings",
    "logo_large",
    "logo_small",
    "make_app",
    "render_header",
    "reset_settings",
    "stamp_approve",
    "stamp_order",
    "stamp_reject",
    "stamp_review",
    "theme",
]

_LAZY_MAP: dict[str, tuple[str, str]] = {
    "Form": ("glory_to_protocol.tui", "Form"),
    "LOGO_LARGE": ("glory_to_protocol.tui.logo", "LOGO_LARGE"),
    "LOGO_SMALL": ("glory_to_protocol.tui.logo", "LOGO_SMALL"),
    "ProtocolSettings": ("glory_to_protocol.settings", "ProtocolSettings"),
    "ProtocolTyper": ("glory_to_protocol.typer", "ProtocolTyper"),
    "ProtocolTyperCommand": ("glory_to_protocol.typer", "ProtocolTyperCommand"),
    "ProtocolTyperGroup": ("glory_to_protocol.typer", "ProtocolTyperGroup"),
    "configure": ("glory_to_protocol.settings", "configure"),
    "get_settings": ("glory_to_protocol.settings", "get_settings"),
    "logo_large": ("glory_to_protocol.tui.logo", "logo_large"),
    "logo_small": ("glory_to_protocol.tui.logo", "logo_small"),
    "make_app": ("glory_to_protocol.typer", "make_app"),
    "render_header": ("glory_to_protocol.tui", "render_header"),
    "reset_settings": ("glory_to_protocol.settings", "reset_settings"),
    "stamp_approve": ("glory_to_protocol.tui", "stamp_approve"),
    "stamp_order": ("glory_to_protocol.tui", "stamp_order"),
    "stamp_reject": ("glory_to_protocol.tui", "stamp_reject"),
    "stamp_review": ("glory_to_protocol.tui", "stamp_review"),
    "theme": ("glory_to_protocol.tui.theme", ""),
}


def __getattr__(name: str) -> object:
    target = _LAZY_MAP.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = target
    module = import_module(module_path)
    return module if attr == "" else getattr(module, attr)
