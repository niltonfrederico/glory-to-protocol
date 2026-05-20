"""Vitrine dos componentes visuais do bureau.

Run with: `uv run protocol-showcase [logo|palette|wrap|jobs|stamps]`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

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
    typer.Option("--save", "-s", help="Salvar saída em arquivo além de exibir."),
]
PathOption = Annotated[
    Path | None,
    typer.Option(
        "--path",
        "-p",
        help="Caminho do arquivo de saída (usado quando --save). Default: logs/tui-<timestamp>.txt",
    ),
]


async def _fake_job(seconds: float) -> None:
    await asyncio.sleep(seconds)


def _render_logo(form: Form) -> None:
    form.line("Logo grande:", style=theme.HEADER)
    for row in LOGO_LARGE.splitlines():
        form.line(row, style=theme.HEADER)
    form.line()
    form.line("Logo pequena:", style=theme.HEADER)
    for row in LOGO_SMALL.splitlines():
        form.line(row, style=theme.CYRILLIC_ACCENT)


def _render_palette(form: Form) -> None:
    form.line("Paleta de estilos:", style=theme.HEADER)
    form.line("BODY — texto padrão do relatório.", style=theme.BODY)
    form.line("MUTED — anotação lateral, contexto secundário.", style=theme.MUTED)
    form.line("CYRILLIC_ACCENT — destaque oficial.", style=theme.CYRILLIC_ACCENT)
    form.line("SIGNATURE — assinatura ao pé.", style=theme.SIGNATURE)


def _render_wrap(form: Form) -> None:
    form.line("Quebra de linha — alfabeto latino:", style=theme.HEADER)
    form.line(
        "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam.",
        style=theme.BODY,
    )
    form.line()
    form.line("Quebra de linha — alfabeto cirílico:", style=theme.HEADER)
    form.line(
        "Бюро вычислительной техники регистрирует входящие директивы Генсека "
        "и обеспечивает их исполнение в установленные сроки без задержек "
        "и без излишних объяснений по существу.",
        style=theme.BODY,
    )
    form.line()
    form.line("Quebra de linha — misto latino + cirílico:", style=theme.HEADER)
    form.line(
        "Norman, Директор NIRVYTEKH, recebeu directive #4711 do Gensek sobre "
        "распределение бюджета entre as quatro diretorias internas do bureau "
        "para o próximo período контроля.",
        style=theme.BODY,
    )


def _render_jobs(form: Form) -> None:
    form.line("Jobs em background (live region):", style=theme.HEADER)
    jobs = [
        Job(
            label="compilando relatório para o Gensek",
            coro_factory=lambda: _fake_job(5.0),
        ),
    ]
    asyncio.run(form.run_pending(jobs))


def _render_stamps(form: Form) -> None:
    form.stamp(stamp_approve("orçamento Q2", "auditoria sem ressalvas"))
    form.stamp(stamp_reject("requisição #4711", "fora do escopo do bureau"))
    form.stamp(stamp_order("mobilização equipe 3", "execução imediata"))
    form.stamp(stamp_review("relatório mensal", "pendente leitura do Gensek"))


def _render_all(form: Form) -> None:
    form.line("Demonstração dos componentes visuais do bureau.", style=theme.MUTED)
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
    "logo": ("Logo grande e pequena.", _render_logo),
    "palette": ("Paleta de estilos do theme.", _render_palette),
    "wrap": ("Quebra de linha em latino, cirílico e misto.", _render_wrap),
    "jobs": ("Jobs em background (live region ticker).", _render_jobs),
    "stamps": ("Carimbos APPROVE / REJECT / ORDER / REVIEW.", _render_stamps),
}

app = typer.Typer(add_completion=False, no_args_is_help=False)


@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    save: SaveOption = False,
    path: PathOption = None,
) -> None:
    """Renderiza componentes de TUI. Sem subcomando, mostra tudo."""
    if ctx.invoked_subcommand is not None:
        return
    _run("tui showcase", _render_all, save, path)


def _register(name: str, render: Callable[[Form], None]) -> Callable[..., None]:
    def cmd(save: SaveOption = False, path: PathOption = None) -> None:
        _run(name, render, save, path)

    return cmd


for _name, (_help, _render) in COMPONENTS.items():
    app.command(_name, help=_help)(_register(_name, _render))


if __name__ == "__main__":
    app()
