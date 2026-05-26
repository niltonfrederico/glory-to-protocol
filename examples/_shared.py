"""Shared building blocks for the example CLIs.

Three runnable entry points (`examples.cli`, `examples.tui`, `examples.hybrid`)
all build the same Typer app from this module and wrap it in a `Protocol`
facade with a different `Mode`. The commands themselves — logo, palette, wrap,
jobs, stamps — are identical across the three variants.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC
from datetime import datetime
from pathlib import Path
from types import FunctionType
from typing import Annotated

import typer
from rich.console import Console

from glory_to_protocol import expose
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.tui import theme
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.logo import LOGO_LARGE
from glory_to_protocol.tui.logo import LOGO_SMALL
from glory_to_protocol.tui.stamps import stamp_approve
from glory_to_protocol.tui.stamps import stamp_order
from glory_to_protocol.tui.stamps import stamp_reject
from glory_to_protocol.tui.stamps import stamp_review

DEFAULT_LOG_DIR = Path("logs")

SaveOption = Annotated[
    bool,
    typer.Option("--save", "-s", help="Save output to file in addition to displaying."),
]
PathOption = Annotated[
    Path | None,
    typer.Option(
        "--path",
        "-p",
        help="Output file path (used with --save). Default: logs/tui-<timestamp>.txt",
    ),
]


async def _fake_job(seconds: float) -> None:
    await asyncio.sleep(seconds)


def _render_logo(form: Form) -> None:
    form.line("Large logo:", style=theme.HEADER)
    for row in LOGO_LARGE.splitlines():
        form.line(row, style=theme.HEADER)
    form.line()
    form.line("Small logo:", style=theme.HEADER)
    for row in LOGO_SMALL.splitlines():
        form.line(row, style=theme.CYRILLIC_ACCENT)


def _render_palette(form: Form) -> None:
    form.line("Style palette:", style=theme.HEADER)
    form.line("BODY — default report body text.", style=theme.BODY)
    form.line("MUTED — side note, secondary context.", style=theme.MUTED)
    form.line("CYRILLIC_ACCENT — official accent.", style=theme.CYRILLIC_ACCENT)
    form.line("SIGNATURE — footer signature.", style=theme.SIGNATURE)


def _render_wrap(form: Form) -> None:
    form.line("Line wrap — Latin alphabet:", style=theme.HEADER)
    form.line(
        "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam.",
        style=theme.BODY,
    )
    form.line()
    form.line("Line wrap — Cyrillic alphabet:", style=theme.HEADER)
    form.line(
        "Бюро вычислительной техники регистрирует входящие директивы Генсека "
        "и обеспечивает их исполнение в установленные сроки без задержек "
        "и без излишних объяснений по существу.",
        style=theme.BODY,
    )
    form.line()
    form.line("Line wrap — Latin + Cyrillic mix:", style=theme.HEADER)
    form.line(
        "Norman, Директор of NIRVYTEKH, received directive #4711 from the Gensek "
        "about распределение бюджета between the bureau's four internal directorates "
        "for the next контроля period.",
        style=theme.BODY,
    )


def _render_jobs(form: Form) -> None:
    form.line("Background jobs (live region):", style=theme.HEADER)
    jobs = [
        Job(
            label="compiling report for the Gensek",
            coro_factory=lambda: _fake_job(5.0),
        ),
    ]
    asyncio.run(form.run_pending(jobs))


def _render_stamps(form: Form) -> None:
    form.stamp(stamp_approve("Q2 budget", "audit clean"))
    form.stamp(stamp_reject("request #4711", "out of bureau scope"))
    form.stamp(stamp_order("team 3 mobilization", "immediate execution"))
    form.stamp(stamp_review("monthly report", "awaiting Gensek review"))


def _render_all(form: Form) -> None:
    form.line("Demonstration of the bureau's visual components.", style=theme.MUTED)
    form.line()
    _render_logo(form)
    form.line()
    _render_palette(form)
    form.line()
    _render_wrap(form)
    form.line()
    _render_jobs(form)
    _render_stamps(form)


def _run(title: str, render: Callable[[Form], None], save: bool, path: Path | None) -> None:
    console = Console(highlight=False, soft_wrap=False, record=save)
    with Form(title=title, console=console) as form:
        render(form)

    if not save:
        return

    target = path
    if target is None:
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%SZ")
        target = DEFAULT_LOG_DIR / f"tui-{stamp}.txt"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    target.write_text(console.export_text(clear=False), encoding="utf-8")
    typer.echo(f"saved → {target}")


COMPONENTS: dict[str, tuple[str, Callable[[Form], None]]] = {
    "logo": ("Large and small logo.", _render_logo),
    "palette": ("Theme style palette.", _render_palette),
    "wrap": ("Line wrapping in Latin, Cyrillic and mixed.", _render_wrap),
    "jobs": ("Background jobs (live region ticker).", _render_jobs),
    "stamps": ("APPROVE / REJECT / ORDER / REVIEW stamps.", _render_stamps),
}

PALETTE_ENTRIES: dict[str, tuple[str, str | None]] = {
    "logo": ("visual", "*"),
    "palette": ("visual", None),
    "wrap": ("visual", None),
    "jobs": ("runtime", "~"),
    "stamps": ("visual", "#"),
}


def _register(name: str, render: Callable[[Form], None]) -> Callable[..., None]:
    def cmd(save: SaveOption = False, path: PathOption = None) -> None:
        _run(name, render, save, path)

    return cmd


def build_app() -> typer.Typer:
    """Return a Typer app with the showcase commands registered."""
    app = typer.Typer(add_completion=False, no_args_is_help=False)

    @app.callback(invoke_without_command=True)
    def default(
        ctx: typer.Context,
        save: SaveOption = False,
        path: PathOption = None,
    ) -> None:
        """Render TUI components. Without a subcommand, shows everything."""
        if ctx.invoked_subcommand is not None:
            return
        _run("tui showcase", _render_all, save, path)

    for name, (help_text, render) in COMPONENTS.items():
        app.command(name, help=help_text)(_register(name, render))

    expose_components(app)
    return app


def expose_components(app: typer.Typer) -> None:
    """Attach `@expose` metadata to every command in `app`."""
    for command_info in app.registered_commands:
        callback = command_info.callback
        if not isinstance(callback, FunctionType):
            continue
        name = command_info.name if command_info.name is not None else callback.__name__
        entry = PALETTE_ENTRIES.get(name)
        if entry is None:
            continue
        section, icon = entry
        help_text, _ = COMPONENTS[name]
        expose(label=name, section=section, icon=icon)(callback)
        callback.__doc__ = help_text
