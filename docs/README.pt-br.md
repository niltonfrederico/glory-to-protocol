<!-- markdownlint-disable MD041 -->

<p align="right">
  <a href="README.md">
    <img src="https://img.shields.io/badge/read%20in-english-6fa86f?style=flat-square" alt="Read in English">
  </a>
</p>

# АРХИВ · Arquivo

A documentação do bureau, organizada em quatro estantes. Escolha a estante pelo que
você precisa agora — não pelo tema do documento.

| Estante | O que faz | Quando abrir |
| --- | --- | --- |
| [Tutoriais](tutorials/) | Caminhada passo a passo. | Primeiro contato. Você nunca construiu nada com a lib. |
| [Guias práticos](how-to/) | Receitas orientadas a tarefa. | Você sabe o que quer fazer e precisa dos passos. |
| [Referência](reference/) | Superfície de API, completa e seca. | Você está escrevendo código e precisa de um nome de campo ou assinatura. |
| [Explicação](explanation/) | Por que a lib tem essa forma. | Você está entre dois caminhos válidos e precisa do critério. |

## Tutoriais

- [**Quickstart**](tutorials/quickstart.pt-br.md) — Construa uma CLI bureau mínima em dez minutos. Stamps, header, um job em background.

## Guias práticos

- [**Modo fallback**](how-to/use-fallback-mode.pt-br.md) — Plugue a facade `Protocol`, escolha um `Mode`, exponha comandos pra paleta interativa, controle o caminho Rich.

## Referência

- [**Settings**](reference/settings.pt-br.md) — `ProtocolSettings`, todos os campos, sub-models, env vars.
- [**Componentes**](reference/components.pt-br.md) — `Form`, `logo_large`, `logo_small`, `theme`, stamps. Assinaturas completas.
- [**Jobs**](reference/jobs.pt-br.md) — `Job`, `JobOutcome`, `JobRunner`, `PipelineRunner`, `PipelineFailed`. Callbacks, guard-rails, semântica.

## Explicação

- [**Modos de dispatch**](explanation/dispatch-modes.pt-br.md) — Por que `Mode` e `Fallback` são eixos separados. O que a capability check realmente checa. Quando o shell Textual entra.

## Índice

Se você veio procurar algo específico:

- As strings cirílicas usadas nos stamps e prompts → [reference/settings.pt-br.md#strings](reference/settings.pt-br.md#strings)
- Como injetar seu próprio logo text → [reference/settings.pt-br.md#override-program%C3%A1tico](reference/settings.pt-br.md#override-program%C3%A1tico)
- Por que `coro_factory` é factory e não coroutine → [reference/jobs.pt-br.md#por-que-uma-factory](reference/jobs.pt-br.md#por-que-uma-factory)
- Ordem de rollback do pipeline em falha parcial → [reference/jobs.pt-br.md#pipelinerunner](reference/jobs.pt-br.md#pipelinerunner)
- O que o extra `[tui]` vai adicionar → [explanation/dispatch-modes.pt-br.md#roadmap](explanation/dispatch-modes.pt-br.md#roadmap)
