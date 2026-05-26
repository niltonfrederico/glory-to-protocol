<!-- markdownlint-disable MD041 MD013 -->

<p align="center">
  <a href="README.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=for-the-badge" alt="Leia em Português">
  </a>
</p>

<p align="center">
  <a href="https://github.com/niltonfrederico/glory-to-protocol/actions/workflows/ci.yml"><img src="https://github.com/niltonfrederico/glory-to-protocol/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/glory-to-protocol/"><img src="https://img.shields.io/pypi/v/glory-to-protocol.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/glory-to-protocol/"><img src="https://img.shields.io/pypi/pyversions/glory-to-protocol.svg" alt="Python versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg" alt="License: AGPL-3.0-or-later"></a>
</p>

<p align="center">
  <img src="assets/svg/header-en-us.svg" alt="glory-to-protocol — Bureau of Computational Technology" width="880">
</p>

## СВОДКА · TL;DR

A Python TUI library for [Typer](https://typer.tiangolo.com/) CLIs that wraps
your commands in a deadpan, state-bureau aesthetic — framed forms, four
decision stamps (`approve` / `reject` / `order` / `review`), themed `--help`,
an ASCII logo header, and a live ticker for background jobs.

`0.3.0` adds the `Protocol` facade, the `@expose` palette decorator, and a
Rich-rendered fallback path. The Textual shell (full interactive surface) lands
in `0.4.0` behind the optional `[tui]` extra.

<p align="center">
  <img src="assets/gifs/showcase.gif" alt="protocol-showcase — all TUI components rendered" width="900">
</p>

## Install

```bash
pip install glory-to-protocol
# or
uv add glory-to-protocol
# or
poetry add glory-to-protocol
```

## 30-second quickstart

```python
import typer
from glory_to_protocol import configure, make_app
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui.stamps import stamp_approve

configure(app_name="MyBureau", logo_text="MyBureau", small_logo_text="MyBureau")
app = make_app()

@app.command()
def status() -> None:
    with Form(title="status") as form:
        form.line("All systems nominal.")
        form.stamp(stamp_approve("status check", "audit clean"))
```

Run with `python my_cli.py status`. For a guided walk-through, see
[**docs/tutorials/quickstart.md**](docs/tutorials/quickstart.md).

## АРХИВ · Documentation

The full bureau archive is in [`docs/`](docs/README.md), sorted by intent:

| Shelf | When to open it |
| --- | --- |
| [Tutorial: quickstart](docs/tutorials/quickstart.md) | First contact. Ten-minute walk-through. |
| [How-to: use fallback mode](docs/how-to/use-fallback-mode.md) | Wire `Protocol` + `Mode` + `@expose` into your CLI. |
| [Reference: settings](docs/reference/settings.md) | Every field on `ProtocolSettings`, with env-var overrides. |
| [Reference: components](docs/reference/components.md) | `Form`, logo, theme, stamps. Signatures and tables. |
| [Reference: jobs](docs/reference/jobs.md) | `JobRunner`, `PipelineRunner`, callbacks, safeguards. |
| [Explanation: dispatch modes](docs/explanation/dispatch-modes.md) | Why `Mode` and `Fallback` are separate axes; the capability check. |

## Status

**Beta (0.3.0).** Public surface is stable enough to drive real CLIs (194
tests, ~98% coverage). Minor versions may still refine APIs before 1.0.

Planned:

- `0.4.0` — Textual shell behind the `[tui]` extra, palette shortcuts.
- `0.5.0+` — Live `JobsTicker` / `LogTail` integration, theming injection, i18n.

Want a favor from the Верховный Лидер (Supreme Leader)?
[Open an issue](https://github.com/niltonfrederico/glory-to-protocol/issues/new).

## ОТКАЗ · Disclaimer

This project's visual and thematic aesthetic is loosely inspired by
[Papers, Please](https://papersplea.se/) (© Lucas Pope / 3909 LLC),
specifically its evocation of a fictional Eastern-Bloc-style state bureau.

The inspiration is atmospheric only. **Glory to Protocol does not use,
reference, or distribute any code, asset, artwork, character, name, country,
or trademark from Papers, Please.** No content from Arstotzka — or any other
fictional element of the game — appears in this repository. The bureau, its
naming, its symbols, and its language are original to this project.

Papers, Please and Arstotzka are property of their respective owners. This
project is not affiliated with, endorsed by, or sponsored by Lucas Pope or
3909 LLC.

If this project's atmosphere resonates with you, please consider supporting
the original creator by buying Papers, Please on its
[official site](https://papersplea.se/) or your preferred storefront.

## Bureau records

- [ВКЛАД · Contributing](CONTRIBUTING.md)
  - [Для граждан повышенного допуска · For citizens of elevated clearance](TRUE_CONTRIBUTING.md)
- [КОДЕКС · Code of Conduct](CODE_OF_CONDUCT.md)
  - [Для граждан повышенного допуска · For citizens of elevated clearance](TRUE_CODE_OF_CONDUCT.md)
- [ЛИЦЕНЗИЯ · License](LICENSE)
