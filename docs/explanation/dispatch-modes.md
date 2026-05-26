<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="dispatch-modes.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# Dispatch modes

The library exposes two configuration knobs that look adjacent but answer
different questions:

- `mode` (`Mode.CLI` / `Mode.TUI` / `Mode.HYBRID`) — **what do you want the
  binary to be?**
- `fallback` (`Fallback.RICH` / `Fallback.ERROR`) — **when the wanted surface
  refuses to load, what should happen?**

This page explains why they are separate.

## What the bureau is, really

A bureau-style CLI has three personas a single binary may need to play:

1. **A scriptable Typer CLI.** `my-bureau ingest --path foo.csv` works in
   shell pipelines, in CI, in cron jobs.
2. **An interactive shell.** `my-bureau` in a terminal opens a Textual app
   with a command palette, forms, live job ticker.
3. **A degraded surface.** Somewhere between the two: piped, sandboxed,
   tiny terminal — still wants to be useful, even if it loses the live UI.

A single binary that can switch between all three is the whole point of the
`Protocol` facade.

## Why two axes

A single setting can't carry the intent honestly. Compare:

- "I want the TUI" doesn't say what to do when the TUI cannot run.
- "Fall back to Rich" doesn't say whether the TUI is the *primary* surface or
  just a nice-to-have when invoked bare.

So the lib splits them:

- `mode` = the **primary preference**.
- `fallback` = the **escape hatch when the preference is unmet**.

`mode` is checked first. `fallback` only matters when `mode` was `tui` or
`hybrid` and the capability check refused.

## The capability check

`Protocol._capability_check()` returns "not ok" when **any** of these is true:

| Failure | Reason |
| --- | --- |
| `sys.stdout` or `sys.stdin` is not a TTY | Piped or non-interactive — no input/output surface to bind a Textual app to. |
| `textual` is not importable | The optional `[tui]` extra was not installed. |
| Terminal smaller than `viewport.min_width × min_height` | Forms and palette would not fit; the experience would be worse than the fallback. |

As of `0.4.0` a passing capability check launches the Textual surface
([`ProtocolApp`](../reference/textual.md)). Earlier (`0.3.0`) the check
returned "not implemented yet" even on a successful probe, so every TUI/HYBRID
invocation traversed the fallback branch. That stub is gone — the live
surface engages as soon as the probe passes.

## The decision tree

```
run(argv)
  │
  ├─ mode == CLI ────────────────────────→ Typer dispatch
  │
  ├─ mode == HYBRID and argv[0] is a subcommand ─→ Typer dispatch
  │
  └─ otherwise:
       capability_check()
         │
         ├─ ok      → ProtocolApp (alt-screen Textual)
         │              ├─ PaletteScreen → FormScreen → app.exit((cb, kwargs))
         │              └─ outcome stamp printed to scrollback (opt-out via show_result_stamp)
         │
         └─ not ok  → fallback:
                       ├─ RICH   → Rich palette + prompt sequence
                       └─ ERROR  → raise ProtocolUnavailable
```

Two things to notice:

1. **`HYBRID` peeks at `argv` before doing anything else.** If the first
   non-flag token names a registered Typer subcommand, the binary stays
   headless — no probing, no header, no palette. This is what makes
   `HYBRID` safe as a default: it does not surprise scripts.
2. **The fallback is not "less than" Textual.** It is a different surface
   designed for non-TTY contexts. Set `Fallback.ERROR` when running without a
   TTY is genuinely wrong (a kiosk binary, an installer).

## Why `expose` is a decorator, not configuration

Commands surface in the interactive palette by carrying an
`__protocol_expose__` attribute, written by `@expose(...)`. Two reasons:

1. **Locality.** The command and its palette metadata live in the same place.
   No registry-elsewhere coupling, no separate manifest to keep in sync with
   the code.
2. **Selective opt-in.** Not every Typer command belongs in the palette — some
   are admin-only, some are wiring details. `@expose` makes the inclusion
   intentional, and `hidden=True` keeps a command callable from the CLI
   without listing it in the palette.

Discovery walks `Typer.registered_commands` at `Protocol(...)` construction
and resolves each callback's `typer_name` against the Typer-declared name,
respecting `@app.command("custom-name")` overrides.

## Roadmap

| Release | What changes |
| --- | --- |
| **0.3.0** | `Protocol`, `expose`, `Mode`, `Fallback`, capability check, Rich fallback. Textual stub returned "not implemented yet" so fallback engaged on every TUI invocation. |
| **0.4.0** (current) | Live Textual surface — `ProtocolApp`, palette, form, help-as-directive, native command palette, result stamp. `BureauTheme` + `LayoutSettings` for identity overrides; `app_factory` for subclassing. |
| **0.5.0+** | Live `JobsTicker` / `LogTail` inside the Textual surface, animated stamps, i18n on footer/status strings. |

When the Textual surface lands in your dependency tree, the skeleton stays
identity-aware: consumers swap `BureauTheme.name`, `logo_text`, accent colors
without touching screens or widgets, and the help overlay reflects the override
through its `directive_prefix` and `sign_off` fields.

## See also

- [How to use fallback mode](../how-to/use-fallback-mode.md) — task-oriented
  walkthrough.
- [Settings reference](../reference/settings.md) — the full configuration
  surface, including env-var overrides.
