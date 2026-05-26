<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="quickstart.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# Quickstart

Ten minutes from `pip install` to a CLI that renders the bureau frame, prints a
stamp, and tracks a background job. No prior knowledge of Typer or Rich
required — you'll learn what you need on the way.

By the end you will have a working `archive` command that:

1. Opens the bureau form frame with the large logo header.
2. Prints a status line.
3. Runs a fake "sync" job in the background with a live ticker.
4. Prints either an `APPROVED` or `REJECTED` stamp based on the outcome.

## Prerequisites

- Python 3.14.
- A clean directory and a virtualenv. `uv venv && source .venv/bin/activate.fish`
  works fine.

## 1. Install the lib

```bash
pip install glory-to-protocol
```

Or, with `uv`:

```bash
uv add glory-to-protocol
```

## 2. Bootstrap the file

Create `bureau.py`:

```python
import typer
from glory_to_protocol import configure, make_app

configure(
    app_name="MyBureau",
    logo_text="MyBureau",
    small_logo_text="MyBureau",
)

app = make_app()
```

`configure(**overrides)` is the canonical coupling point between your CLI and
the lib — it mutates the settings singleton. `make_app()` returns a
`typer.Typer()` pre-wired with the bureau's themed `--help` renderer.

Run it once to confirm it works:

```bash
python bureau.py --help
```

You should see the gold-leaf help banner. If it crashes with
`InvalidASCIICharactersError`, you passed a character outside the default
ASCII alphabet to `logo_text` — uppercase A–Z and digits only.

## 3. Add a first command with a Form

Append:

```python
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui import theme

@app.command()
def status() -> None:
    """Print the current bureau status."""
    with Form(title="status") as form:
        form.line("All systems nominal.", style=theme.BODY)
        form.line("Director on duty.", style=theme.MUTED)
```

Run:

```bash
python bureau.py status
```

You should see the bureau frame, the logo header, two body lines, and the
signature footer.

## 4. Print a stamp

Stamps are the bureau's terminal decisions. Add:

```python
from glory_to_protocol.tui.stamps import stamp_approve, stamp_reject

@app.command()
def review(reject: bool = False) -> None:
    """Pretend to review a request and stamp it."""
    with Form(title="review") as form:
        form.line("Examining request #4711...", style=theme.MUTED)
        if reject:
            form.stamp(stamp_reject("request #4711", "out of bureau scope"))
        else:
            form.stamp(stamp_approve("request #4711", "audit clean"))
```

```bash
python bureau.py review            # APPROVED
python bureau.py review --reject   # REJECTED
```

## 5. Run a background job

The lib ships with an async job runner that renders a live ticker. Add:

```python
import asyncio
from glory_to_protocol.jobs.types import Job

async def fake_sync() -> None:
    await asyncio.sleep(2)

@app.command()
def archive() -> None:
    """Archive the day's ledger entries."""
    with Form(title="archive") as form:
        form.line("Reconciling with central archive...", style=theme.MUTED)
        outcomes = asyncio.run(
            form.run_pending([
                Job(label="syncing ledger", coro_factory=fake_sync),
            ])
        )

    failed = any(o.status == "fail" for o in outcomes)
    with Form(title="archive · result", show_header=False) as form:
        if failed:
            form.stamp(stamp_reject("archive", "sync failed"))
        else:
            form.stamp(stamp_approve("archive", "ledger reconciled"))
```

Note two things:

- `coro_factory=fake_sync` passes the **function**, not its result. The runner
  calls the factory when it spawns the job. Passing `fake_sync()` instead
  would bind the coroutine to the wrong event loop. See
  [reference/jobs.md#why-a-factory](../reference/jobs.md#why-a-factory).
- The second `Form` uses `show_header=False` so you do not get a duplicate
  logo block in the result frame.

Run it:

```bash
python bureau.py archive
```

You should see the first frame open, a live ticker count down two seconds,
then the result frame with an `APPROVED` stamp.

## 6. Wire as a console script

Move `bureau.py` into a package and add to your `pyproject.toml`:

```toml
[project.scripts]
my-bureau = "my_package.bureau:app"
```

Now `my-bureau status`, `my-bureau review`, `my-bureau archive` are real
commands in your environment.

## What's next

- **The interactive surface** — wrap `app` in a `Protocol` facade with
  `Mode.HYBRID` and add `@expose` to your commands. See
  [how-to/use-fallback-mode.md](../how-to/use-fallback-mode.md).
- **Custom branding** — change the logo, director, signature, and stamps via
  `configure()`. See [reference/settings.md](../reference/settings.md).
- **More components** — `theme.HEADER`, `theme.CYRILLIC_ACCENT`, line wrap,
  pipeline rollback. See [reference/components.md](../reference/components.md)
  and [reference/jobs.md](../reference/jobs.md).
