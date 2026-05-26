<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="dispatch-modes.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# Modos de dispatch

A lib expõe dois botões de configuração que parecem adjacentes mas respondem
perguntas diferentes:

- `mode` (`Mode.CLI` / `Mode.TUI` / `Mode.HYBRID`) — **o que você quer que o
  binário seja?**
- `fallback` (`Fallback.RICH` / `Fallback.ERROR`) — **quando a superfície
  desejada se recusa a carregar, o que deve acontecer?**

Essa página explica por que eles são separados.

## O que o bureau é, na verdade

Uma CLI estilo bureau tem três personas que um único binário pode precisar
encarnar:

1. **Uma Typer CLI scriptável.** `my-bureau ingest --path foo.csv` funciona em
   pipelines, CI, cron.
2. **Um shell interativo.** `my-bureau` em terminal abre uma Textual app com
   paleta de comandos, forms, ticker ao vivo.
3. **Uma superfície degradada.** Entre os dois: piped, sandboxed, terminal
   pequeno — ainda quer ser útil, mesmo perdendo a UI ao vivo.

Um único binário que troca entre os três é o ponto inteiro da facade
`Protocol`.

## Por que dois eixos

Uma configuração só não carrega a intenção honestamente. Compare:

- "Quero o TUI" não diz o que fazer quando o TUI não roda.
- "Fall back pra Rich" não diz se o TUI é a superfície *primária* ou apenas um
  nice-to-have quando invocado nu.

Então a lib separa:

- `mode` = a **preferência primária**.
- `fallback` = o **escape quando a preferência não é atendida**.

`mode` é checado primeiro. `fallback` só importa quando `mode` era `tui` ou
`hybrid` e a capability check recusou.

## A capability check

`Protocol._capability_check()` retorna "not ok" quando **qualquer uma** destas
é verdade:

| Falha | Razão |
| --- | --- |
| `sys.stdout` ou `sys.stdin` não é TTY | Piped ou não-interativo — sem superfície de I/O pra prender a Textual app. |
| `textual` não importa | O extra opcional `[tui]` não foi instalado. |
| Terminal menor que `viewport.min_width × min_height` | Forms e paleta não caberiam; a experiência seria pior que o fallback. |

A partir do `0.4.0`, uma capability check bem-sucedida sobe a superfície Textual
([`ProtocolApp`](../reference/textual.pt-br.md)). Antes (`0.3.0`) a check
retornava "not implemented yet" mesmo numa probe ok, então toda invocação
TUI/HYBRID atravessava o fallback. Esse stub foi removido — a superfície ao
vivo engata assim que a probe passa.

## A árvore de decisão

```
run(argv)
  │
  ├─ mode == CLI ────────────────────────→ dispatch Typer
  │
  ├─ mode == HYBRID e argv[0] é subcommand ─→ dispatch Typer
  │
  └─ caso contrário:
       capability_check()
         │
         ├─ ok      → ProtocolApp (alt-screen Textual)
         │              ├─ PaletteScreen → FormScreen → app.exit((cb, kwargs))
         │              └─ stamp de resultado no scrollback (opt-out via show_result_stamp)
         │
         └─ not ok  → fallback:
                       ├─ RICH   → paleta Rich + prompts
                       └─ ERROR  → levanta ProtocolUnavailable
```

Duas coisas a notar:

1. **`HYBRID` espia `argv` antes de qualquer coisa.** Se o primeiro token não-
   flag nomeia um subcommand do Typer, o binário fica headless — sem probe,
   sem header, sem paleta. É isso que torna `HYBRID` seguro como default: não
   surpreende scripts.
2. **O fallback não é "menos que" o Textual.** É uma superfície diferente,
   feita pra contextos não-TTY. Use `Fallback.ERROR` quando rodar sem TTY é
   genuinamente errado (kiosk binary, installer).

## Por que `expose` é decorator, não configuração

Comandos aparecem na paleta interativa carregando um atributo
`__protocol_expose__`, escrito por `@expose(...)`. Duas razões:

1. **Localidade.** O comando e o metadado da paleta vivem no mesmo lugar. Sem
   coupling com registry-em-outro-lugar, sem manifest separado pra manter
   sincronizado com o código.
2. **Opt-in seletivo.** Nem todo comando Typer pertence à paleta — alguns são
   admin-only, alguns são wiring interno. `@expose` torna a inclusão
   intencional, e `hidden=True` mantém um comando callable pela CLI sem
   listá-lo na paleta.

A discovery percorre `Typer.registered_commands` na construção do `Protocol(...)`
e resolve o `typer_name` de cada callback contra o nome declarado no Typer,
respeitando overrides tipo `@app.command("custom-name")`.

## Roadmap

| Release | O que muda |
| --- | --- |
| **0.3.0** | `Protocol`, `expose`, `Mode`, `Fallback`, capability check, fallback Rich. Stub Textual retornava "not implemented yet" então o fallback engatava em toda invocação TUI. |
| **0.4.0** (atual) | Superfície Textual ao vivo — `ProtocolApp`, paleta, form, help-as-despacho, command palette nativa, stamp de resultado. `BureauTheme` + `LayoutSettings` pra overrides de identidade; `app_factory` pra subclasse. |
| **0.5.0+** | `JobsTicker` / `LogTail` ao vivo dentro da superfície Textual, stamps animados, i18n no footer/status strings. |

Quando a superfície Textual está disponível na árvore de dependências, o
esqueleto continua identity-aware: consumers trocam `BureauTheme.name`,
`logo_text`, accent colors sem tocar em screens ou widgets, e o overlay de
help reflete o override via `directive_prefix` e `sign_off`.

## Veja também

- [Como usar modo fallback](../how-to/use-fallback-mode.pt-br.md) — caminhada
  orientada a tarefa.
- [Referência de settings](../reference/settings.pt-br.md) — a superfície de
  configuração completa, incluindo overrides por env var.
