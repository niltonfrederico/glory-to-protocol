<p align="center">
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/read%20in-english-c0392b?style=for-the-badge" alt="Read in English">
  </a>
</p>

# Contribuição

Obrigado por considerar contribuir. Esta página é curta de propósito. Se
você curte a voz do bureau, as mesmas regras vivem em
[TRUE_CONTRIBUTING.pt-br.md](TRUE_CONTRIBUTING.pt-br.md).

## Antes de começar

Leia o [Código de Conduta](CODE_OF_CONDUCT.pt-br.md). Ele é aplicado — em
especial a seção de
[Tolerância Zero](CODE_OF_CONDUCT.pt-br.md#tolerância-zero).

## Toda mudança começa como uma issue

Feature, bug, refactor, docs — tudo começa com uma issue. Nada de PR
drive-by; se um aparecer sem issue linkada, o primeiro comentário de review
vai ser um pedido pra abrir uma. O ponto não é burocracia, é que o desenho
da mudança seja discutido antes de alguém escrever código que não vai dar
merge.

Um PR endereça uma issue. Não embuta um refactor num PR de feature.

## Padrão de qualidade

Um PR está pronto pra review quando:

- Os testes passam.
- A cobertura não regride.
- `ruff format` e `ruff check` estão limpos.
- `ty` (type check) está limpo.
- Testes novos seguem `test_should_{expected}_when_{condition}`.

Se um check falha por motivo não relacionado ao seu patch, declare isso na
descrição do PR em vez de desabilitar o check.

## Assistência de IA

Ferramentas de IA são bem-vindas aqui. Construí a maior parte desta
biblioteca ao lado do Claude — intensamente, abertamente, com a mão em
cada diff. Então não vou fingir que não uso, e não tenho interesse em
policiar se você usa.

O que eu peço: **seja AI-assisted, não vibe-coder.** Concretamente:

- Leia o diff antes de abrir o PR. Se você não consegue explicar uma linha,
  não envie.
- Entenda o teste que você escreveu. Testes gerados que ninguém leu são
  piores que ausência de testes.
- Assuma o código. *"Foi a IA que escreveu"* não é resposta a uma pergunta
  de review.

Se um PR tem a cara de código que ninguém leu antes de sair, ele é fechado
com pedido pra refazer.

## Reuso antes de duplicação

Antes de adicionar um novo helper, função ou componente, busque no
codebase algo que já faça aquilo (ou quase faça). Estenda ou refatore a
coisa existente primeiro — duplicação é a opção mais cara ao longo da vida
do projeto.

Duas âncoras:

- [PEP 8](https://peps.python.org/pep-0008/) — *"código é lido muito mais
  do que é escrito."* Nomenclatura, layout e consistência existem porque o
  próximo leitor é o centro de custo.
- [PEP 20, o Zen do Python](https://peps.python.org/pep-0020/) —
  particularmente *"Deveria haver uma — e preferencialmente apenas uma —
  maneira óbvia de fazer isso,"* e *"Esparso é melhor que denso."*

Três linhas parecidas é melhor que uma abstração prematura. Três funções
quase idênticas não.

## Abrindo o PR

- Linke a issue.
- Descreva a mudança em duas ou três frases — o *porquê*, não uma
  recapitulação do diff.
- Note qualquer trabalho de follow-up conscientemente adiado.

É isso. Bem-vindo(a).
