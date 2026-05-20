<p align="center">
  <a href="CONTRIBUTING.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=for-the-badge" alt="Leia em Português">
  </a>
</p>

# Contributing

Thanks for considering a contribution. This page is short on purpose. If you
enjoy the bureau voice, the same rules live in
[TRUE_CONTRIBUTING.md](TRUE_CONTRIBUTING.md).

## Before you start

Read the [Code of Conduct](CODE_OF_CONDUCT.md). It is enforced — the
[Zero Tolerance](CODE_OF_CONDUCT.md#zero-tolerance) section in particular.

## Every change starts as an issue

Feature, bug, refactor, docs — all of it begins with an issue. No drive-by
PRs; if one shows up without a linked issue, the first review comment will
be a request to file one. The point isn't bureaucracy, it's so the design
gets discussed before anyone writes code that won't merge.

One PR addresses one issue. Don't bundle a refactor into a feature PR.

## Quality bar

A PR is ready for review when:

- `uv run pre-commit run --all-files` is clean (covers lint, format, type
  check, dead fixtures, markdown).
- Tests pass and coverage does not regress.
- New tests follow `test_should_{expected}_when_{condition}`.

If a check fails for reasons unrelated to your patch, call it out in the PR
description rather than disabling the check.

## AI assistance

AI tooling is welcome here. I built most of this library alongside Claude —
heavily, openly, with my hands on every diff. So I'm not going to pretend I
don't, and I have no interest in policing whether you do.

What I do ask: **be AI-assisted, not vibe-coded.** Concretely:

- Read the diff before opening the PR. If you can't explain a line, don't
  ship it.
- Understand the test you wrote. Generated tests that nobody read are worse
  than no tests at all.
- Own the code. "The AI wrote it" is not an answer to a review question.

If a PR has the shape of code nobody read on the way out, it will be closed
with a request for a do-over.

## Reuse before you duplicate

Before adding a new helper, function, or component, search the codebase for
something that already does it (or almost does it). Extend or refactor the
existing thing first — duplication is the more expensive option over the
project's life.

Two anchors:

- [PEP 8](https://peps.python.org/pep-0008/) — *"code is read much more
  often than it is written."* Naming, layout, and consistency exist because
  the next reader is the cost center.
- [PEP 20, the Zen of Python](https://peps.python.org/pep-0020/) —
  particularly *"There should be one — and preferably only one — obvious way
  to do it,"* and *"Sparse is better than dense."*

Three similar lines beats a premature abstraction. Three near-identical
functions does not.

## Filing the PR

- Link the issue.
- Describe the change in two or three sentences — the *why*, not a recap of
  the diff.
- Note any follow-up work consciously deferred.

That's it. Welcome.
