<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="components.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Componentes

Tudo que renderiza na lib vive dentro de (ou compõe com) um `Form` — a moldura
do bureau é a unidade de apresentação.

## `Form`

`from glory_to_protocol.tui.forms import Form`

Context manager que desenha a moldura do bureau (borda superior, header,
divisor, corpo, assinatura, borda inferior).

```python
with Form(title="version") as form:
    form.line("Consultando os registros do bureau...")
```

### Construtor

| Parâmetro | Tipo | Default | Propósito |
| --- | --- | --- | --- |
| `title` | `str` | — | Rótulo na aba da borda superior. Posicional. |
| `console` | `Console \| None` | `None` | Injeta uma `Console` do Rich; criada automaticamente se omitida. |
| `show_header` | `bool` | `True` | Renderiza o bloco logo grande + título do bureau no topo. |
| `signature_text` | `str \| None` | `None` | Sobrescreve a assinatura do rodapé; default vem de `settings.director_signature`. |

### Métodos

| Método | Assinatura | Efeito |
| --- | --- | --- |
| `line` | `(text: str = "", style: Style \| None = None, *, wrap: bool = True)` | Imprime uma linha emoldurada. `wrap=False` trunca em vez de quebrar. |
| `divider` | `()` | Imprime um divisor horizontal dentro da moldura. |
| `stamp` | `(renderable: RenderableType)` | Imprime qualquer renderable do Rich dentro da moldura — usado com os helpers `stamp_*`. |
| `run_pending` | `async (jobs: list[Job]) -> list[JobOutcome]` | Fan-out de jobs com ticker ao vivo; retorna os outcomes quando todos chegam em estado terminal. Veja [jobs.pt-br.md](jobs.pt-br.md). |

## `logo_large` / `logo_small`

`from glory_to_protocol.tui.logo import logo_large, logo_small`

Renderizadores ASCII guiados por `settings.logo_text` e `settings.small_logo_text`.

```python
print(logo_large())            # usa settings.logo_text
print(logo_small("ARCHIVE"))   # override explícito
```

### Assinaturas

```python
def logo_large(text: str | None = None) -> str: ...
def logo_small(text: str | None = None) -> str: ...
```

Passar `None` lê as settings atuais. Os resultados são memoizados;
`configure(**overrides)` invalida o cache.

As constantes de módulo `LOGO_LARGE` e `LOGO_SMALL` são strings pré-renderizadas
pro default `logo_text="Protocol"`; use quando você não precisa de override e
quer pular a chamada de função.

## `theme`

`from glory_to_protocol.tui import theme`

`Style` nomeados do Rich pra tipografia consistente entre componentes.

```python
form.line("Corpo padrão do relatório.",     style=theme.BODY)
form.line("Nota lateral, contexto.",         style=theme.MUTED)
form.line("Acento oficial.",                 style=theme.CYRILLIC_ACCENT)
form.line("Linha de assinatura.",            style=theme.SIGNATURE)
```

### Papéis

| Style | Papel |
| --- | --- |
| `theme.HEADER` | Títulos de seção, tipografia dourada. |
| `theme.BODY` | Corpo padrão do relatório. |
| `theme.MUTED` | Notas laterais, contexto secundário. |
| `theme.CYRILLIC_ACCENT` | Acento oficial (vermelho do bureau). |
| `theme.SIGNATURE` | Linha de assinatura do rodapé (itálico cinza). |
| `theme.BORDER` | A própria moldura. |
| `theme.STAMP_APPROVE` | Usado por `stamp_approve`. |
| `theme.STAMP_REJECT` | Usado por `stamp_reject`. |
| `theme.STAMP_ORDER` | Usado por `stamp_order`. |
| `theme.STAMP_REVIEW` | Usado por `stamp_review`. |

Também exposto: `theme.FORM_WIDTH = 80` — a largura interna que a moldura desenha.

## Stamps

`from glory_to_protocol.tui.stamps import stamp_approve, stamp_reject, stamp_order, stamp_review`

Quatro variantes que codificam as decisões terminais do bureau sobre um pedido.
Cada uma aceita um `label` obrigatório e um `detail` opcional, retornando um
`Table` do Rich pronto pra `Form.stamp()`.

```python
form.stamp(stamp_approve("orçamento Q2", "auditoria limpa"))
form.stamp(stamp_reject("pedido #4711", "fora do escopo do bureau"))
form.stamp(stamp_order("mobilização da equipe 3", "execução imediata"))
form.stamp(stamp_review("relatório mensal", "aguardando revisão do Gensek"))
```

### Variantes

| Função | Label (RU / EN) | Use para |
| --- | --- | --- |
| `stamp_approve` | `ОДОБРЕНО / APPROVED` | Pedido concedido, ação completa. |
| `stamp_reject` | `ОТКАЗАНО / REJECTED` | Pedido negado; coloque a razão em `detail`. |
| `stamp_order` | `ПРИКАЗ / DIRECT ORDER` | Imperativo — o bureau está ditando uma ação. |
| `stamp_review` | `К СВЕДЕНИЮ / FOR REVIEW` | Aguardando decisão externa (ex.: do Gensek). |

Assinatura: `stamp_<variant>(label: str, detail: str = "") -> Table`.

## Comportamento de wrap

`Form.line(text)` faz cell-wrap pra largura interna da moldura, tratando
conteúdo latino, cirílico e misto corretamente:

```python
form.line(texto_longo)                # default: wrap pra largura interna
form.line(texto_longo, wrap=False)    # trunca pra uma linha
```

Com `wrap=False`, uma linha maior que a largura interna é truncada pra caber;
nenhuma elipse é inserida.

## Re-exports públicos

O pacote no topo re-exporta os nomes mais usados pra consumidores não terem que
lembrar dos caminhos de submódulo:

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

Tudo importa lazy — puxar um nome não importa os outros.

## Superfície Textual

`Form`, `logo_*`, `stamp_*`, e `render_header` são os componentes Rich-side.
Renderizam em qualquer Console (incluindo o fallback) e dentro de widgets
Textual via `Static(rich_renderable)`.

Os widgets Textual-nativos (`OfficialHeader`, `BindingsFooter`, `PaletteScreen`,
`FormScreen`, `HelpOverlay`, `ProtocolApp`) são documentados em
[`textual.pt-br.md`](textual.pt-br.md). Pra receitas (troca de tema, screens
custom, overrides via env vars), veja
[`how-to/customize-tui.pt-br.md`](../how-to/customize-tui.pt-br.md).
