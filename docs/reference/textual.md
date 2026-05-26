<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="textual.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# Reference: Textual surface

The fullscreen alt-screen UI shipped in `0.4.0`. Built on [Textual](https://textual.textualize.io/),
configurable through `BureauTheme` and `LayoutSettings`, extensible through `app_factory`.

## Dispatch

When `protocol.run()` resolves to `Mode.TUI` (or `Mode.HYBRID` with empty argv) and the
[capability check](../explanation/dispatch-modes.md#capability-check) passes, the facade
instantiates a `ProtocolApp` via the configured `app_factory` (default: `ProtocolApp`),
runs it in alt-screen, and dispatches the operator's chosen callback after the app exits.
The result stamp prints to the terminal scrollback after the dispatch returns.

## `ProtocolApp`

```python
from glory_to_protocol import Protocol, ProtocolApp

class MyApp(ProtocolApp):
    pass

protocol = Protocol(typer_app=app, app_factory=MyApp)
```

Constructor: `ProtocolApp(protocol: Protocol)`. Subclass to add screens, change CSS, or
add bindings. The default app composes three regions:

| Region | Widget | Source of truth |
| --- | --- | --- |
| Header | `OfficialHeader` | `LayoutSettings.bureau.name`, `bureau.subtitle`, `bureau.logo_text`, `layout.logo_size` |
| Body | `PaletteScreen` ⇄ `FormScreen` | `protocol.exposed`, `fields_from_typer(click_cmd)` |
| Footer | `BindingsFooter` | `LayoutSettings.bureau.footer_labels` |

Overlays (`HelpOverlay`, native command palette) push on top via `App.push_screen`.

## Default bindings

| Key | Action | Where |
| --- | --- | --- |
| `j` / `k` | Move cursor up/down in palette | `PaletteScreen` |
| `enter` | Select highlighted row | `DataTable` default |
| `/` | Focus the filter input | `PaletteScreen` |
| `?` | Open help-as-directive overlay | `ProtocolApp` |
| `escape` | Close overlay / cancel form | `HelpOverlay` / `FormScreen` |
| `ctrl+\` | Open the native command palette | Textual built-in |
| `q` | Quit | Textual built-in |

Override via `LayoutSettings.keybinds` (see [Recipe 2](../how-to/customize-tui.md#recipe-2-override-keybinds)).

## `BureauTheme`

Frozen Pydantic model holding the identity surface. Every field has an env-var override
through `PROTOCOL_LAYOUT__BUREAU__<FIELD>`.

| Field | Type | Default | Purpose |
| --- | --- | --- | --- |
| `name` | `str` | `"NIRVYTEKH"` | Bureau short name shown in header / despacho |
| `subtitle` | `str` | `"Bureau of Computational Technology"` | Header subtitle |
| `logo_text` | `str` | `"NIRVYTEKH"` | Text rendered as ASCII logo |
| `accent` | `str` | `"#c0392b"` | Border + accent color (red) |
| `gold` | `str` | `"#d4af37"` | Logo + emphasis color |
| `bg` | `str` | `"#000000"` | Background |
| `border` | `str` | `"#7a7a7a"` | Inputs + dividers |
| `muted` | `str` | `"#6c7a89"` | Secondary text |
| `text_color` | `str` | `"#e6e6e6"` | Default body text |
| `status_strings` | `dict[str, str]` | `ready/working/done/error/cancelled` (Cyrillic) | Status labels |
| `footer_labels` | `dict[str, str]` | English labels | Footer key captions |
| `directive_prefix` | `str` | `"ДИРЕКТИВА №"` | Help overlay header |
| `sign_off` | `str` | `"S chestyu, NIRVYTEKH"` | Help overlay footer |

The default `status_strings` keys: `ready`, `working`, `done`, `error`, `cancelled`.
The default `footer_labels` keys: `quit`, `help`, `palette`, `select`, `back`, `filter`.

## `LayoutSettings`

Nested under `ProtocolSettings.layout`.

| Field | Type | Default | Purpose |
| --- | --- | --- | --- |
| `bureau` | `BureauTheme` | `BureauTheme()` | Identity surface |
| `logo_size` | `"small" \| "medium" \| "large"` | `"medium"` | Logo variant in header |
| `keybinds` | `dict[str, str]` | `{quit, help, back, filter}` defaults | Action → key mapping |
| `show_result_stamp` | `bool` | `True` | Print outcome stamp after dispatch |

## Public exports

```python
from glory_to_protocol import (
    ProtocolApp,
    PaletteScreen,
    FormScreen,
    HelpOverlay,
    OfficialHeader,
    BindingsFooter,
    ExposedCommandProvider,
    BureauTheme,
    LayoutSettings,
    render_result_stamp,
)
```

## Color palette

The visual palette is lifted from `assets/svg/header-en-us.svg` so the printable
documents and the live surface match:

| Variable | Hex | Source |
| --- | --- | --- |
| `$bg` | `#000000` | Background |
| `$accent` | `#c0392b` | Stamp + title red |
| `$gold` | `#d4af37` | Logo |
| `$border` | `#7a7a7a` | Frame line |
| `$muted` | `#6c7a89` | Meta line, footer |
| `$text-color` | `#e6e6e6` | Body |

These are injected via `ProtocolApp.get_css_variables()` and consumed in every widget's
`DEFAULT_CSS`.
