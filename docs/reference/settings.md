<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="settings.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# `ProtocolSettings`

Backed by `pydantic-settings`. One singleton, mutated through `configure(**kwargs)`
at startup. Every field is also overridable via environment variable
(`PROTOCOL_` prefix, `__` for nested fields).

```python
from glory_to_protocol import ProtocolSettings, configure, get_settings

configure(app_name="MyBureau")       # mutate the singleton
settings = get_settings()             # read the current snapshot
```

## Field summary

| Field | Type | Default |
| --- | --- | --- |
| `app_name` | `str` | `"Protocol"` |
| `logo_text` | `str` | `"Protocol"` |
| `small_logo_text` | `str` | `"Protocol"` |
| `bureau_title` | `str` | `"БЮРО NIRVYTEKH · Bureau of Computational Technology"` |
| `director_name` | `str` | `"Норман"` |
| `director_signature` | `str` | `"Подписано: Норман, Директор NIRVYTEKH"` |
| `ascii` | [`ASCIISettings`](#asciisettings) | `ASCIISettings()` |
| `mode` | [`Mode`](#mode) | `Mode.HYBRID` |
| `fallback` | [`Fallback`](#fallback) | `Fallback.RICH` |
| `palette` | [`PaletteSettings`](#palettesettings) | `PaletteSettings()` |
| `viewport` | [`ViewportSettings`](#viewportsettings) | `ViewportSettings()` |
| `strings` | [`Strings`](#strings) | `Strings()` |

`logo_text` is validated against `ascii.allowed_characters` at construction time;
characters outside the set raise `InvalidASCIICharactersError`.

## `Mode`

`StrEnum`. Members:

| Member | Value | What dispatch does |
| --- | --- | --- |
| `Mode.CLI` | `"cli"` | Always run as a Typer CLI. No fallback path. |
| `Mode.TUI` | `"tui"` | Always try Textual first. If unavailable, follow `fallback`. |
| `Mode.HYBRID` | `"hybrid"` | If `argv` names a subcommand, run CLI. Otherwise try Textual. |

Importable as `from glory_to_protocol import Mode`.

## `Fallback`

`StrEnum`. Members:

| Member | Value | Effect when Textual is unavailable |
| --- | --- | --- |
| `Fallback.RICH` | `"rich"` | Degrade to a Rich-rendered palette + prompt sequence. |
| `Fallback.ERROR` | `"error"` | Raise `ProtocolUnavailable` with the failure reason. |

Importable as `from glory_to_protocol import Fallback`.

## `ASCIISettings`

| Field | Type | Default |
| --- | --- | --- |
| `allowed_alphabet` | `set[str]` | Uppercase A–Z, 0–9 (from `_ascii.ALPHABET`). |
| `allowed_symbols` | `set[str]` | `{"★", ":star:"}` |
| `allowed_misc` | `set[str]` | `{" "}` |
| `allowed_characters` | `set[str]` (computed) | Union of the three. |

Override either set to widen what `logo_text` and `small_logo_text` will accept.

## `PaletteSettings`

| Field | Type | Default |
| --- | --- | --- |
| `shortcut` | `str` | `"ctrl+k"` |
| `placeholder` | `str` | `"Type a command…"` |

Consumed by the interactive palette (lands with the Textual shell in 0.4.0).

## `ViewportSettings`

| Field | Type | Default | Constraint |
| --- | --- | --- | --- |
| `min_width` | `int` | `80` | `>= 20` |
| `min_height` | `int` | `24` | `>= 10` |
| `require_fullscreen` | `bool` | `False` | — |

The capability check rejects terminals smaller than `min_width × min_height`,
triggering the fallback path.

## `Strings`

Five subgroups. Defaults are Cyrillic, matching the bureau aesthetic.
Importable as `from glory_to_protocol import Strings`.

### `Strings.stamps` (`StampStrings`)

| Field | Default |
| --- | --- |
| `approved` | `"ОДОБРЕНО"` |
| `rejected` | `"ОТКАЗАНО"` |
| `pending` | `"В ОЧЕРЕДИ"` |

### `Strings.palette` (`PaletteStrings`)

| Field | Default |
| --- | --- |
| `title` | `"ДИРЕКТИВЫ"` |
| `empty` | `"Нет директив."` |
| `placeholder` | `"Найти директиву…"` |

### `Strings.forms` (`FormStrings`)

| Field | Default |
| --- | --- |
| `submit` | `"ОТПРАВИТЬ"` |
| `cancel` | `"ОТМЕНИТЬ"` |
| `required` | `"Обязательное поле"` |

### `Strings.header` (`HeaderStrings`)

| Field | Default |
| --- | --- |
| `motto` | `"Слава ПРОТОКОЛУ"` |

### `Strings.viewport` (`ViewportStrings`)

| Field | Default |
| --- | --- |
| `too_small_title` | `"ОКНО СЛИШКОМ МАЛО"` |
| `too_small_body` | `"Требуется {min_w}×{min_h}. Текущее: {cur_w}×{cur_h}."` |
| `fullscreen_hint` | `"ПОЛНЫЙ ЭКРАН РЕКОМЕНДУЕТСЯ"` |

## Programmatic override

The canonical coupling point between an embedding CLI and the lib.

```python
from glory_to_protocol import Mode, Strings, configure

configure(
    app_name="MyBureau",
    logo_text="MyBureau",
    small_logo_text="MyBureau",
    director_name="Ada Lovelace",
    director_signature="Signed: Ada Lovelace, Director",
    mode=Mode.CLI,
    strings=Strings(),
)
```

Each call **merges** overrides on top of the current singleton — unspecified
fields keep their value. Derived caches (logo memoization) are invalidated
automatically.

For test isolation, `reset_settings()` clears the singleton back to defaults.

## Environment variables

Every field is also addressable through the environment. Prefix is `PROTOCOL_`;
nested fields use `__` as the delimiter.

| Env var | Maps to |
| --- | --- |
| `PROTOCOL_APP_NAME` | `app_name` |
| `PROTOCOL_LOGO_TEXT` | `logo_text` |
| `PROTOCOL_MODE` | `mode` |
| `PROTOCOL_FALLBACK` | `fallback` |
| `PROTOCOL_PALETTE__SHORTCUT` | `palette.shortcut` |
| `PROTOCOL_VIEWPORT__MIN_WIDTH` | `viewport.min_width` |
| `PROTOCOL_STRINGS__STAMPS__APPROVED` | `strings.stamps.approved` |
| `PROTOCOL_STRINGS__PALETTE__TITLE` | `strings.palette.title` |

Env vars are read at `ProtocolSettings()` construction time. If you call
`configure(**kwargs)` after the singleton is already constructed, the kwargs
override the env vars.

## Singleton accessors

```python
from glory_to_protocol import get_settings, configure
from glory_to_protocol.settings import reset_settings
```

| Function | What it does |
| --- | --- |
| `get_settings()` | Returns the current singleton; constructs it on first call. |
| `configure(**overrides)` | Merges overrides, invalidates derived caches, returns the new snapshot. |
| `reset_settings()` | Test helper. Drops the singleton; next `get_settings()` rebuilds it from env / defaults. |
