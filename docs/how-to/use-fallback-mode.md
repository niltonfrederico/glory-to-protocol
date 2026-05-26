<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="use-fallback-mode.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# How to use fallback mode

You want your CLI to feel interactive when run from a real terminal, and stay
scriptable when piped or used in CI. This guide wires the `Protocol` facade and
the Rich fallback path to do exactly that.

For background on **why** the dispatch surface is shaped as two axes (mode +
fallback), see [explanation/dispatch-modes.md](../explanation/dispatch-modes.md).

## Prerequisites

- A working Typer app — anything that builds a `typer.Typer()` instance with
  one or more `@app.command()`-registered functions.
- A `ProtocolSettings` (or willingness to take the defaults).

## Step 1 — wrap your Typer app

Replace your existing entry point with a `Protocol` facade.

```python
import typer
from glory_to_protocol import Mode, Protocol, ProtocolSettings

app = typer.Typer()

@app.command()
def status() -> None:
    print("All systems nominal.")

protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.HYBRID),
)

def main() -> None:
    protocol.run()
```

Wire `main` as your console script in `pyproject.toml`:

```toml
[project.scripts]
my-bureau = "my_package.cli:main"
```

## Step 2 — pick the dispatch mode

`mode` decides what `Protocol.run()` tries first.

| `Mode` | Behaviour |
| --- | --- |
| `Mode.CLI` | Always Typer. No interactive surface. Use for binaries that must stay headless. |
| `Mode.TUI` | Always try Textual. If unavailable, follow `fallback`. |
| `Mode.HYBRID` | If `argv` names a subcommand, Typer. Otherwise try Textual. Default. |

`HYBRID` is the right default for most CLIs: `my-bureau status` keeps working,
while bare `my-bureau` lifts you into the interactive palette.

```python
ProtocolSettings(mode=Mode.HYBRID)
```

You can also set it from the environment:

```bash
PROTOCOL_MODE=cli my-bureau
```

## Step 3 — expose commands to the palette

Add `@expose` to any command you want listed in the interactive palette. The
decorator goes **above** `@app.command()` so Typer sees the wrapped callback.

```python
from glory_to_protocol import expose

@app.command()
@expose(section="data", icon="◈")
def ingest(path: str, dry_run: bool = False) -> None:
    """Ingest a file into the ledger."""
    ...
```

`expose` reads the function's docstring first line as the palette description,
and uses the function name (kebab-cased) as the default label.

| Kwarg | Effect |
| --- | --- |
| `label` | Override the displayed name. |
| `section` | Group commands under a heading. |
| `shortcut` | Bind a keyboard shortcut (validated for collisions). |
| `icon` | Single-character icon. |
| `hidden` | Keep callable from the CLI, omit from the palette. |

Shortcut collisions raise `ValueError` at `Protocol(...)` construction time.

## Step 4 — choose what happens when Textual cannot run

`fallback` decides what `Protocol.run()` does when the capability check fails.

| `Fallback` | Effect |
| --- | --- |
| `Fallback.RICH` | Degrade to a Rich-rendered numbered palette + `rich.prompt` form sequence. |
| `Fallback.ERROR` | Raise `ProtocolUnavailable` with the reason. |

```python
from glory_to_protocol import Fallback, Mode, ProtocolSettings

ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH)
```

The capability check fails when any of these is true:

- `sys.stdout` or `sys.stdin` is not a TTY (piped, CI).
- The `textual` package is not importable.
- The terminal is smaller than `settings.viewport.min_width × min_height`.

**In 0.3.0**, the check also fails for "textual surface not implemented yet" —
the Textual shell lands in 0.4.0 alongside the `[tui]` extra. Until then every
`tui`/`hybrid` invocation falls through to the Rich path (or raises, depending
on `fallback`).

## Step 5 — observe the fallback path

In a piped or CI context the dispatcher will:

1. Print the bureau header.
2. List exposed commands numbered 1..N.
3. Prompt for the index.
4. Build a Rich prompt sequence from the command's parameters (defaults,
   choices, and `--help` strings are honoured).
5. Invoke the underlying callback with the collected values.

Force the fallback locally by piping the binary:

```bash
my-bureau | cat
```

Or by shrinking your terminal below the configured viewport floor.

## Strict mode for CI

Set `Fallback.ERROR` in environments where running without a TTY should be a
hard error:

```python
ProtocolSettings(mode=Mode.TUI, fallback=Fallback.ERROR)
```

Useful for binaries that must refuse to run without an interactive surface —
the dispatcher raises `ProtocolUnavailable` with the failure reason, which
your top-level handler can turn into a non-zero exit code.

## Putting it all together

```python
import typer
from glory_to_protocol import (
    Fallback,
    Mode,
    Protocol,
    ProtocolSettings,
    expose,
)

app = typer.Typer()

@app.command()
@expose(section="data", icon="◈")
def ingest(path: str, dry_run: bool = False) -> None:
    """Ingest a file into the ledger."""
    ...

@app.command()
@expose(section="report")
def report() -> None:
    """Print the latest bureau report."""
    ...

protocol = Protocol(
    typer_app=app,
    settings=ProtocolSettings(mode=Mode.HYBRID, fallback=Fallback.RICH),
)

def main() -> None:
    protocol.run()
```

- `my-bureau ingest --path foo.csv` → straight Typer dispatch.
- `my-bureau` in a terminal → (0.4.0+) Textual shell; today → Rich fallback.
- `my-bureau | cat` → Rich fallback (numbered palette + prompts).
- With `Fallback.ERROR`, the last two become `ProtocolUnavailable` instead.
