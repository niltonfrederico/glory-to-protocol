<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="components.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# Components

Every renderable in the lib sits inside (or works with) a `Form` — the bureau
frame is the unit of presentation.

## `Form`

`from glory_to_protocol.tui.forms import Form`

Context manager that draws the bureau form frame (top border, header,
divider, body, signature, bottom border).

```python
with Form(title="version") as form:
    form.line("Consulting bureau records...")
```

### Constructor

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `title` | `str` | — | Tab label on the top border. Positional. |
| `console` | `Console \| None` | `None` | Inject a Rich `Console`; auto-created if omitted. |
| `show_header` | `bool` | `True` | Render the large logo + bureau title block at the top. |
| `signature_text` | `str \| None` | `None` | Override the footer signature; defaults to `settings.director_signature`. |

### Methods

| Method | Signature | Effect |
| --- | --- | --- |
| `line` | `(text: str = "", style: Style \| None = None, *, wrap: bool = True)` | Print one bordered line. `wrap=False` truncates instead of wrapping. |
| `divider` | `()` | Print a horizontal divider inside the frame. |
| `stamp` | `(renderable: RenderableType)` | Print any Rich renderable inside the frame — used with the `stamp_*` helpers. |
| `run_pending` | `async (jobs: list[Job]) -> list[JobOutcome]` | Fan out jobs with a live ticker; returns outcomes when all jobs reach a terminal state. See [jobs.md](jobs.md). |

## `logo_large` / `logo_small`

`from glory_to_protocol.tui.logo import logo_large, logo_small`

ASCII logo renderers driven by `settings.logo_text` and `settings.small_logo_text`.

```python
print(logo_large())            # uses settings.logo_text
print(logo_small("ARCHIVE"))   # explicit override
```

### Signatures

```python
def logo_large(text: str | None = None) -> str: ...
def logo_small(text: str | None = None) -> str: ...
```

Passing `None` reads the current settings. Results are memoized;
`configure(**overrides)` invalidates the cache.

The module-level constants `LOGO_LARGE` and `LOGO_SMALL` are pre-rendered
strings for the default `logo_text="Protocol"`; use them when you don't need
override semantics and want to skip the function call.

## `theme`

`from glory_to_protocol.tui import theme`

Named Rich `Style` objects for consistent typography across components.

```python
form.line("Default report body.",       style=theme.BODY)
form.line("Side note, secondary.",      style=theme.MUTED)
form.line("Official accent.",           style=theme.CYRILLIC_ACCENT)
form.line("Footer signature line.",     style=theme.SIGNATURE)
```

### Roles

| Style | Role |
| --- | --- |
| `theme.HEADER` | Section headings, gold-leaf typography. |
| `theme.BODY` | Default report body. |
| `theme.MUTED` | Side notes, secondary context. |
| `theme.CYRILLIC_ACCENT` | Official accent (bureau red). |
| `theme.SIGNATURE` | Footer signature line (italic gray). |
| `theme.BORDER` | The form frame itself. |
| `theme.STAMP_APPROVE` | Used by `stamp_approve`. |
| `theme.STAMP_REJECT` | Used by `stamp_reject`. |
| `theme.STAMP_ORDER` | Used by `stamp_order`. |
| `theme.STAMP_REVIEW` | Used by `stamp_review`. |

Also exposed: `theme.FORM_WIDTH = 80` — the inner width the frame draws to.

## Stamps

`from glory_to_protocol.tui.stamps import stamp_approve, stamp_reject, stamp_order, stamp_review`

Four variants encode the bureau's terminal decisions on a request. Each takes a
required `label` and an optional `detail`, returning a Rich `Table` ready for
`Form.stamp()`.

```python
form.stamp(stamp_approve("Q2 budget", "audit clean"))
form.stamp(stamp_reject("request #4711", "out of bureau scope"))
form.stamp(stamp_order("team 3 mobilization", "immediate execution"))
form.stamp(stamp_review("monthly report", "awaiting Gensek review"))
```

### Variants

| Function | Label (RU / EN) | Use for |
| --- | --- | --- |
| `stamp_approve` | `ОДОБРЕНО / APPROVED` | Request granted, action complete. |
| `stamp_reject` | `ОТКАЗАНО / REJECTED` | Request denied; include `detail` with the reason. |
| `stamp_order` | `ПРИКАЗ / DIRECT ORDER` | Imperative — the bureau is dictating an action. |
| `stamp_review` | `К СВЕДЕНИЮ / FOR REVIEW` | Awaiting external decision (e.g., from the Gensek). |

Signature: `stamp_<variant>(label: str, detail: str = "") -> Table`.

## Wrap behaviour

`Form.line(text)` cell-wraps to the form's inner width, handling Latin,
Cyrillic, and mixed-alphabet content correctly:

```python
form.line(long_text)                # default: wrap to inner width
form.line(long_text, wrap=False)    # truncate to one line
```

When `wrap=False`, a line longer than the inner width is truncated to fit; no
ellipsis is inserted.

## Public re-exports

The top-level package re-exports the most-used names so consumers don't have to
remember submodule paths:

```python
from glory_to_protocol import (
    Form,
    LOGO_LARGE,
    LOGO_SMALL,
    logo_large,
    logo_small,
    render_header,
    stamp_approve,
    stamp_reject,
    stamp_order,
    stamp_review,
)
```

Everything imports lazily — pulling one name does not import the rest.
