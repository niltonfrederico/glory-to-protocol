<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="settings.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# `ProtocolSettings`

Construído sobre `pydantic-settings`. Um singleton, mutável via
`configure(**kwargs)` no boot. Todo campo também aceita override por variável
de ambiente (prefixo `PROTOCOL_`, `__` pra campos aninhados).

```python
from glory_to_protocol import ProtocolSettings, configure, get_settings

configure(app_name="MyBureau")       # muta o singleton
settings = get_settings()             # lê o snapshot atual
```

## Resumo de campos

| Campo | Tipo | Default |
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

`logo_text` é validado contra `ascii.allowed_characters` na construção; caracteres
fora do conjunto disparam `InvalidASCIICharactersError`.

## `Mode`

`StrEnum`. Membros:

| Membro | Valor | O que o dispatcher faz |
| --- | --- | --- |
| `Mode.CLI` | `"cli"` | Sempre roda como Typer CLI. Sem fallback. |
| `Mode.TUI` | `"tui"` | Sempre tenta Textual primeiro. Se indisponível, segue `fallback`. |
| `Mode.HYBRID` | `"hybrid"` | Se `argv` nomeia um subcommand, vai pra CLI. Senão tenta Textual. |

Importável como `from glory_to_protocol import Mode`.

## `Fallback`

`StrEnum`. Membros:

| Membro | Valor | Efeito quando Textual indisponível |
| --- | --- | --- |
| `Fallback.RICH` | `"rich"` | Degrada pra paleta Rich + prompts sequenciais. |
| `Fallback.ERROR` | `"error"` | Lança `ProtocolUnavailable` com a razão da falha. |

Importável como `from glory_to_protocol import Fallback`.

## `ASCIISettings`

| Campo | Tipo | Default |
| --- | --- | --- |
| `allowed_alphabet` | `set[str]` | A–Z maiúsculo, 0–9 (vem de `_ascii.ALPHABET`). |
| `allowed_symbols` | `set[str]` | `{"★", ":star:"}` |
| `allowed_misc` | `set[str]` | `{" "}` |
| `allowed_characters` | `set[str]` (computado) | União dos três. |

Sobrescreva qualquer um dos conjuntos pra ampliar o que `logo_text` e
`small_logo_text` aceitam.

## `PaletteSettings`

| Campo | Tipo | Default |
| --- | --- | --- |
| `shortcut` | `str` | `"ctrl+k"` |
| `placeholder` | `str` | `"Type a command…"` |

Consumido pela paleta interativa (entra com o shell Textual em 0.4.0).

## `ViewportSettings`

| Campo | Tipo | Default | Restrição |
| --- | --- | --- | --- |
| `min_width` | `int` | `80` | `>= 20` |
| `min_height` | `int` | `24` | `>= 10` |
| `require_fullscreen` | `bool` | `False` | — |

A capability check rejeita terminais menores que `min_width × min_height`,
disparando o caminho de fallback.

## `LayoutSettings`

A identidade da superfície Textual. Documentação completa em
[`docs/reference/textual.pt-br.md`](textual.pt-br.md); resumo nível
`ProtocolSettings`:

| Campo | Tipo | Default | Função |
| --- | --- | --- | --- |
| `bureau` | `BureauTheme` | Defaults NIRVYTEKH | Logo text, nome, accent, labels do footer, strings do despacho |
| `logo_size` | `"small" \| "medium" \| "large"` | `"medium"` | Variante do logo no `OfficialHeader` |
| `keybinds` | `dict[str, str]` | `{quit:q, help:question_mark, back:escape, filter:slash}` | Mapping ação → tecla |
| `show_result_stamp` | `bool` | `True` | Imprime stamp de outcome em todo dispatch |

Override por env: `PROTOCOL_LAYOUT__BUREAU__ACCENT='#00ffea'`,
`PROTOCOL_LAYOUT__LOGO_SIZE=large`, etc.

## `Strings`

Cinco subgrupos. Defaults são cirílicos, batendo com a estética do bureau.
Importável como `from glory_to_protocol import Strings`.

### `Strings.stamps` (`StampStrings`)

| Campo | Default |
| --- | --- |
| `approved` | `"ОДОБРЕНО"` |
| `rejected` | `"ОТКАЗАНО"` |
| `pending` | `"В ОЧЕРЕДИ"` |

### `Strings.palette` (`PaletteStrings`)

| Campo | Default |
| --- | --- |
| `title` | `"ДИРЕКТИВЫ"` |
| `empty` | `"Нет директив."` |
| `placeholder` | `"Найти директиву…"` |

### `Strings.forms` (`FormStrings`)

| Campo | Default |
| --- | --- |
| `submit` | `"ОТПРАВИТЬ"` |
| `cancel` | `"ОТМЕНИТЬ"` |
| `required` | `"Обязательное поле"` |

### `Strings.header` (`HeaderStrings`)

| Campo | Default |
| --- | --- |
| `motto` | `"Слава ПРОТОКОЛУ"` |

### `Strings.viewport` (`ViewportStrings`)

| Campo | Default |
| --- | --- |
| `too_small_title` | `"ОКНО СЛИШКОМ МАЛО"` |
| `too_small_body` | `"Требуется {min_w}×{min_h}. Текущее: {cur_w}×{cur_h}."` |
| `fullscreen_hint` | `"ПОЛНЫЙ ЭКРАН РЕКОМЕНДУЕТСЯ"` |

## Override programático

O ponto canônico de acoplamento entre a CLI hospedeira e a lib.

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

Cada chamada **mescla** os overrides em cima do singleton — campos não passados
mantêm o valor. Caches derivados (memoização de logo) são invalidados
automaticamente.

Pra isolamento em testes, `reset_settings()` zera o singleton.

## Variáveis de ambiente

Todo campo também é endereçável pelo ambiente. Prefixo `PROTOCOL_`; campos
aninhados usam `__`.

| Env var | Mapeia para |
| --- | --- |
| `PROTOCOL_APP_NAME` | `app_name` |
| `PROTOCOL_LOGO_TEXT` | `logo_text` |
| `PROTOCOL_MODE` | `mode` |
| `PROTOCOL_FALLBACK` | `fallback` |
| `PROTOCOL_PALETTE__SHORTCUT` | `palette.shortcut` |
| `PROTOCOL_VIEWPORT__MIN_WIDTH` | `viewport.min_width` |
| `PROTOCOL_STRINGS__STAMPS__APPROVED` | `strings.stamps.approved` |
| `PROTOCOL_STRINGS__PALETTE__TITLE` | `strings.palette.title` |

Env vars são lidas na construção do `ProtocolSettings()`. Se você chamar
`configure(**kwargs)` depois do singleton já ter sido construído, os kwargs
sobrepõem as env vars.

## Acesso ao singleton

```python
from glory_to_protocol import get_settings, configure
from glory_to_protocol.settings import reset_settings
```

| Função | O que faz |
| --- | --- |
| `get_settings()` | Retorna o singleton atual; constrói na primeira chamada. |
| `configure(**overrides)` | Mescla overrides, invalida caches derivados, retorna o snapshot novo. |
| `reset_settings()` | Helper de teste. Limpa o singleton; próxima `get_settings()` reconstrói do env / defaults. |
