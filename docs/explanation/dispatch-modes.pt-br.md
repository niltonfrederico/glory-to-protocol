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

Em 0.3.0 a check também retorna "not ok" por uma razão placeholder — a
superfície Textual ainda não foi construída. Isso é intencional: o encanamento
do dispatch entra em 0.3.0 pra CLIs hospedeiras já poderem ligar `Protocol`
nos seus entry points; a Textual app em si entra em 0.4.0 junto com o extra
`[tui]`. Até lá, toda invocação `tui`/`hybrid` atravessa o ramo de fallback.

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
         ├─ ok      → (0.4.0+) shell Textual
         │           (0.3.0)  cai pro fallback, "not implemented yet"
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
| **0.3.0** (atual) | `Protocol`, `expose`, `Mode`, `Fallback`, capability check, fallback Rich. Caminho Textual retorna "not implemented yet" então o fallback engaja em toda invocação TUI. |
| **0.4.0** | Shell Textual atrás do extra `[tui]`. `mode=Mode.TUI` e `mode=Mode.HYBRID` nu abrem paleta + forms ao vivo. |
| **0.5.0+** | Integração com `JobsTicker` / `LogTail` ao vivo, atalhos de paleta (`ctrl+k`), botões de injeção de tema, i18n. |

O salto 0.3.0 → 0.4.0 não deve exigir mudanças de código em CLIs hospedeiras:
o mesmo encanamento `Protocol(typer_app=..., settings=...)` segue funcionando.
Adicionar `glory-to-protocol[tui]` nas dependências instala Textual e levanta
o veredito da capability check.

## Veja também

- [Como usar modo fallback](../how-to/use-fallback-mode.pt-br.md) — caminhada
  orientada a tarefa.
- [Referência de settings](../reference/settings.pt-br.md) — a superfície de
  configuração completa, incluindo overrides por env var.
