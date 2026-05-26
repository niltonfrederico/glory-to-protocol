from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import EllipsisType
from typing import Any

import click

_TYPER_INTERNAL_PARAMS = frozenset({"help", "install_completion", "show_completion"})


@dataclass(frozen=True, slots=True)
class FormField:
    name: str
    annotation: type
    default: Any | EllipsisType
    help: str
    choices: tuple[str, ...] | None
    multiple: bool
    hidden: bool


def fields_from_typer(cmd: click.Command) -> list[FormField]:
    """Extract a list of FormField from a click.Command (Typer-built).

    Skips Typer auto-params (--help, --install-completion, --show-completion)
    and any param marked hidden.
    """
    fields: list[FormField] = []
    for param in cmd.params:
        if not isinstance(param, (click.Argument, click.Option)):
            continue
        if param.name is None:
            continue
        if isinstance(param, click.Option) and param.name in _TYPER_INTERNAL_PARAMS:
            continue
        if getattr(param, "hidden", False):
            continue
        default = Ellipsis if param.required or param.default is None else param.default
        nargs = getattr(param, "nargs", 1)
        multiple = bool(getattr(param, "multiple", False)) or nargs not in (1, None)
        fields.append(
            FormField(
                name=param.name,
                annotation=_annotation_for(param),
                default=default,
                help=getattr(param, "help", "") or "",
                choices=_choices_from(param),
                multiple=multiple,
                hidden=False,
            )
        )
    return fields


def _choices_from(param: click.Parameter) -> tuple[str, ...] | None:
    if isinstance(param.type, click.Choice):
        return tuple(str(c) for c in param.type.choices)
    return None


def _annotation_for(param: click.Parameter) -> type:
    ptype = param.type
    if isinstance(ptype, click.types.BoolParamType):
        return bool
    if isinstance(ptype, click.types.IntParamType):
        return int
    if isinstance(ptype, click.types.FloatParamType):
        return float
    if isinstance(ptype, click.Path):
        return Path
    return str
