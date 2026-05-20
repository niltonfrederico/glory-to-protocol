from typing import Any

import typer

from glory_to_protocol.tui.help import ProtocolTyperCommand
from glory_to_protocol.tui.help import ProtocolTyperGroup


class ProtocolTyper(typer.Typer):
    """Typer flavor that themes both groups and leaf commands via the bureau TUI."""

    def command(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("cls", ProtocolTyperCommand)
        return super().command(*args, **kwargs)

    def add_typer(self, typer_instance: typer.Typer, *args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("cls", ProtocolTyperGroup)
        return super().add_typer(typer_instance, *args, **kwargs)


def make_app(**kwargs: Any) -> ProtocolTyper:
    """Build a ProtocolTyper app that prints --help instead of erroring on no args.

    Use this for every command namespace (root and sub-apps) so the UX is
    consistent: invoking the app or a sub-app with nothing else shows the
    help for that level. Help itself is rendered via the bureau's TUI.
    """
    kwargs.setdefault("no_args_is_help", True)
    kwargs.setdefault("cls", ProtocolTyperGroup)
    return ProtocolTyper(**kwargs)


__all__ = ["ProtocolTyper", "ProtocolTyperCommand", "ProtocolTyperGroup", "make_app"]
