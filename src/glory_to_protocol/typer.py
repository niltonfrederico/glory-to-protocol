from typing import Any

import typer

from glory_to_protocol.tui.help import NormanTyperCommand
from glory_to_protocol.tui.help import NormanTyperGroup


class NormanTyper(typer.Typer):
    """Typer flavor that themes both groups and leaf commands via the bureau TUI."""

    def command(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("cls", NormanTyperCommand)
        return super().command(*args, **kwargs)


def make_app(**kwargs: Any) -> NormanTyper:
    """Build a NormanTyper app that prints --help instead of erroring on no args.

    Use this for every command namespace (root and sub-apps) so the UX is
    consistent: invoking the app or a sub-app with nothing else shows the
    help for that level. Help itself is rendered via the bureau's TUI.
    """
    kwargs.setdefault("no_args_is_help", True)
    kwargs.setdefault("cls", NormanTyperGroup)
    return NormanTyper(**kwargs)


__all__ = ["NormanTyper", "NormanTyperCommand", "NormanTyperGroup", "make_app"]
