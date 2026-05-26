<!-- markdownlint-disable MD041 -->

<p align="right">
  <a href="README.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# АРХИВ · Archive

The bureau's documentation, sorted into four shelves. Pick the shelf that matches what
you need right now — not what the document is about.

| Shelf | What it does | When to open it |
| --- | --- | --- |
| [Tutorials](tutorials/) | Hand-holding walkthroughs. | First contact. You've never built anything with this library. |
| [How-to guides](how-to/) | Task-oriented recipes. | You know what you want to do, you need the steps. |
| [Reference](reference/) | API surface, full and dry. | You're writing code and need a field name or signature. |
| [Explanation](explanation/) | Why the lib is shaped this way. | You're picking between two valid approaches and need the rationale. |

## Tutorials

- [**Quickstart**](tutorials/quickstart.md) — Build a minimal bureau CLI in ten minutes. Stamps, header, one background job.

## How-to guides

- [**Use fallback mode**](how-to/use-fallback-mode.md) — Wire the `Protocol` facade, pick a `Mode`, expose commands to the interactive palette, control the Rich fallback path.
- [**Customize the TUI**](how-to/customize-tui.md) — Swap the `BureauTheme`, override keybinds, subclass `ProtocolApp` to add your own screens.

## Reference

- [**Settings**](reference/settings.md) — `ProtocolSettings`, every field, every sub-model, every env var.
- [**Components**](reference/components.md) — `Form`, `logo_large`, `logo_small`, `theme`, stamps. Full signatures.
- [**Jobs**](reference/jobs.md) — `Job`, `JobOutcome`, `JobRunner`, `PipelineRunner`, `PipelineFailed`. Callbacks, safeguards, semantics.
- [**Textual surface**](reference/textual.md) — `ProtocolApp`, `BureauTheme`, `LayoutSettings`, default bindings, color palette.

## Explanation

- [**Dispatch modes**](explanation/dispatch-modes.md) — Why `Mode` and `Fallback` are separate axes. What the capability check actually checks. How the Textual surface fits in.

## Index

If you came looking for something specific:

- The Cyrillic strings used in stamps and prompts → [reference/settings.md#strings](reference/settings.md#strings)
- How to inject your own logo text → [reference/settings.md#programmatic-override](reference/settings.md#programmatic-override)
- Why `coro_factory` is a factory and not a coroutine → [reference/jobs.md#why-a-factory](reference/jobs.md#why-a-factory)
- Pipeline rollback order on partial failure → [reference/jobs.md#pipelinerunner](reference/jobs.md#pipelinerunner)
- What the `[tui]` extra will add → [explanation/dispatch-modes.md#roadmap](explanation/dispatch-modes.md#roadmap)
