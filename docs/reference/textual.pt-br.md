<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="textual.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Referência: Superfície Textual

A UI fullscreen alt-screen entregue no `0.4.0`. Construída sobre [Textual](https://textual.textualize.io/),
configurável via `BureauTheme` e `LayoutSettings`, extensível via `app_factory`.

## Dispatch

Quando `protocol.run()` cai em `Mode.TUI` (ou `Mode.HYBRID` com argv vazio) e a
[capability check](../explanation/dispatch-modes.pt-br.md#capability-check) passa, a facade
instancia uma `ProtocolApp` via o `app_factory` configurado (default: `ProtocolApp`),
roda em alt-screen, e dispatcha o callback escolhido pelo operador depois que a app sai.
O stamp de resultado imprime no scrollback do terminal logo após o dispatch retornar.

## `ProtocolApp`

```python
from glory_to_protocol import Protocol, ProtocolApp

class MyApp(ProtocolApp):
    pass

protocol = Protocol(typer_app=app, app_factory=MyApp)
```

Construtor: `ProtocolApp(protocol: Protocol)`. Subclasse pra adicionar screens, mudar CSS
ou adicionar bindings. A app default compõe três regiões:

| Região | Widget | Fonte da verdade |
| --- | --- | --- |
| Header | `OfficialHeader` | `LayoutSettings.bureau.name`, `bureau.subtitle`, `bureau.logo_text`, `layout.logo_size` |
| Body | `PaletteScreen` ⇄ `FormScreen` | `protocol.exposed`, `fields_from_typer(click_cmd)` |
| Footer | `BindingsFooter` | `LayoutSettings.bureau.footer_labels` |

Overlays (`HelpOverlay`, command palette nativa) push em cima via `App.push_screen`.

## Bindings default

| Tecla | Ação | Onde |
| --- | --- | --- |
| `j` / `k` | Move cursor na palette | `PaletteScreen` |
| `enter` | Seleciona linha destacada | `DataTable` default |
| `/` | Foca o filtro | `PaletteScreen` |
| `?` | Abre overlay help-as-despacho | `ProtocolApp` |
| `escape` | Fecha overlay / cancela form | `HelpOverlay` / `FormScreen` |
| `ctrl+\` | Abre a command palette nativa | Textual built-in |
| `q` | Sair | Textual built-in |

Sobrescreva via `LayoutSettings.keybinds` (veja [Receita 2](../how-to/customize-tui.pt-br.md#receita-2-sobrescrever-keybinds)).

## `BureauTheme`

Pydantic model frozen com a superfície de identidade. Todo campo tem env override via
`PROTOCOL_LAYOUT__BUREAU__<CAMPO>`.

| Campo | Tipo | Default | Função |
| --- | --- | --- | --- |
| `name` | `str` | `"NIRVYTEKH"` | Nome curto do bureau no header / despacho |
| `subtitle` | `str` | `"Bureau of Computational Technology"` | Subtítulo do header |
| `logo_text` | `str` | `"NIRVYTEKH"` | Texto renderizado como logo ASCII |
| `accent` | `str` | `"#c0392b"` | Borda + accent (vermelho) |
| `gold` | `str` | `"#d4af37"` | Logo + ênfase |
| `bg` | `str` | `"#000000"` | Background |
| `border` | `str` | `"#7a7a7a"` | Inputs + divisores |
| `muted` | `str` | `"#6c7a89"` | Texto secundário |
| `text_color` | `str` | `"#e6e6e6"` | Texto default |
| `status_strings` | `dict[str, str]` | `ready/working/done/error/cancelled` (cirílico) | Labels de status |
| `footer_labels` | `dict[str, str]` | Labels em inglês | Legendas do footer |
| `directive_prefix` | `str` | `"ДИРЕКТИВА №"` | Header do overlay de help |
| `sign_off` | `str` | `"S chestyu, NIRVYTEKH"` | Footer do overlay de help |

Chaves default de `status_strings`: `ready`, `working`, `done`, `error`, `cancelled`.
Chaves default de `footer_labels`: `quit`, `help`, `palette`, `select`, `back`, `filter`.

## `LayoutSettings`

Nested em `ProtocolSettings.layout`.

| Campo | Tipo | Default | Função |
| --- | --- | --- | --- |
| `bureau` | `BureauTheme` | `BureauTheme()` | Superfície de identidade |
| `logo_size` | `"small" \| "medium" \| "large"` | `"medium"` | Variante do logo no header |
| `keybinds` | `dict[str, str]` | `{quit, help, back, filter}` defaults | Mapping ação → tecla |
| `show_result_stamp` | `bool` | `True` | Imprime stamp de resultado pós-dispatch |

## Exports públicos

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

## Paleta de cores

A paleta visual vem de `assets/svg/header-en-us.svg` pra documentos impressos e
superfície ao vivo combinarem:

| Variável | Hex | Origem |
| --- | --- | --- |
| `$bg` | `#000000` | Background |
| `$accent` | `#c0392b` | Stamp + título vermelho |
| `$gold` | `#d4af37` | Logo |
| `$border` | `#7a7a7a` | Linha do frame |
| `$muted` | `#6c7a89` | Meta line, footer |
| `$text-color` | `#e6e6e6` | Body |

Injetadas via `ProtocolApp.get_css_variables()` e consumidas no `DEFAULT_CSS` de cada
widget.
