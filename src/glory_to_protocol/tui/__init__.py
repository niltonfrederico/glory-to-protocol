from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from glory_to_protocol.tui import theme
    from glory_to_protocol.tui.forms import Form
    from glory_to_protocol.tui.header import render_header
    from glory_to_protocol.tui.logo import logo_large
    from glory_to_protocol.tui.logo import logo_small
    from glory_to_protocol.tui.stamps import stamp_approve
    from glory_to_protocol.tui.stamps import stamp_order
    from glory_to_protocol.tui.stamps import stamp_reject
    from glory_to_protocol.tui.stamps import stamp_review

__all__ = [
    "LOGO_LARGE",
    "LOGO_SMALL",
    "Form",
    "logo_large",
    "logo_small",
    "render_header",
    "stamp_approve",
    "stamp_order",
    "stamp_reject",
    "stamp_review",
    "theme",
]

_LAZY_MAP: dict[str, tuple[str, str]] = {
    "Form": ("glory_to_protocol.tui.forms", "Form"),
    "LOGO_LARGE": ("glory_to_protocol.tui.logo", "LOGO_LARGE"),
    "LOGO_SMALL": ("glory_to_protocol.tui.logo", "LOGO_SMALL"),
    "logo_large": ("glory_to_protocol.tui.logo", "logo_large"),
    "logo_small": ("glory_to_protocol.tui.logo", "logo_small"),
    "render_header": ("glory_to_protocol.tui.header", "render_header"),
    "stamp_approve": ("glory_to_protocol.tui.stamps", "stamp_approve"),
    "stamp_order": ("glory_to_protocol.tui.stamps", "stamp_order"),
    "stamp_reject": ("glory_to_protocol.tui.stamps", "stamp_reject"),
    "stamp_review": ("glory_to_protocol.tui.stamps", "stamp_review"),
    "theme": ("glory_to_protocol.tui.theme", ""),
}


def __getattr__(name: str) -> object:
    target = _LAZY_MAP.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = target
    module = import_module(module_path)
    return module if attr == "" else getattr(module, attr)
