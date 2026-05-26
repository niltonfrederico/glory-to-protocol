from __future__ import annotations

import inspect
from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import replace
from typing import Any
from typing import Protocol as _TypingProtocol
from typing import TypeVar
from typing import runtime_checkable

import typer


@runtime_checkable
class _Named(_TypingProtocol):
    __name__: str
    __doc__: str | None

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


F = TypeVar("F", bound=_Named)

EXPOSE_ATTR = "__protocol_expose__"


@dataclass(frozen=True, slots=True)
class ExposedCommand:
    callback: Callable[..., Any]
    typer_name: str
    label: str
    section: str | None
    shortcut: str | None
    description: str
    form: type | None
    icon: str | None
    hidden: bool


def _kebab(name: str) -> str:
    return name.replace("_", "-")


def _humanize(name: str) -> str:
    return name.replace("_", " ")


def _first_doc_line(func: _Named) -> str:
    doc = inspect.getdoc(func) or ""
    return doc.splitlines()[0] if doc else ""


def expose(
    *,
    label: str | None = None,
    section: str | None = None,
    shortcut: str | None = None,
    form: type | None = None,
    icon: str | None = None,
    hidden: bool = False,
) -> Callable[[F], F]:
    """Annotate a Typer callback as exposed to the interactive shell.

    Writes an :class:`ExposedCommand` into ``func.__protocol_expose__``.
    The Protocol facade discovers exposed callbacks at run-time by
    walking the Typer app.
    """

    def wrap(func: F) -> F:
        info = ExposedCommand(
            callback=func,
            typer_name=_kebab(func.__name__),
            label=label or _humanize(func.__name__),
            section=section,
            shortcut=shortcut,
            description=_first_doc_line(func),
            form=form,
            icon=icon,
            hidden=hidden,
        )
        setattr(func, EXPOSE_ATTR, info)
        return func

    return wrap


def discover_exposed(app: typer.Typer) -> list[ExposedCommand]:
    """Walk a Typer app and collect ExposedCommand annotations.

    Raises ``ValueError`` when two exposed commands share the same shortcut.
    """
    exposed: list[ExposedCommand] = []
    for command_info in app.registered_commands:
        callback = command_info.callback
        if callback is None:
            continue
        info = getattr(callback, EXPOSE_ATTR, None)
        if info is None:
            continue
        resolved_name = command_info.name or info.typer_name
        if resolved_name != info.typer_name:
            info = replace(info, typer_name=resolved_name)
        exposed.append(info)
    _validate_shortcuts(exposed)
    return exposed


def palette_entries(exposed: Iterable[ExposedCommand]) -> list[ExposedCommand]:
    """Subset of exposed commands that should appear in the palette."""
    return [e for e in exposed if not e.hidden]


def _validate_shortcuts(exposed: list[ExposedCommand]) -> None:
    seen: dict[str, str] = {}
    for entry in exposed:
        if entry.shortcut is None:
            continue
        previous = seen.get(entry.shortcut)
        if previous is not None:
            raise ValueError(
                f"Shortcut collision: '{entry.shortcut}' bound by "
                f"'{previous}' and '{getattr(entry.callback, '__name__', '<anon>')}'"
            )
        seen[entry.shortcut] = getattr(entry.callback, "__name__", "<anon>")
