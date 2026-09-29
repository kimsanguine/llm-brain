---
name: llm-brain
description: Work with this repository's provenance-preserving second-brain workflow. Use for llm-brain setup, source ingestion, curation, grounded query, expression, OKF export, or safe diagnostics.
---

# llm-brain

Use this skill only from the cloned `llm-brain` repository. It gives Codex the same workflow boundary as the Claude Code plugin; it does not change the wiki-web service's configured LLM runtime.

## Start safely

1. Read `CLAUDE.md` before any operation that can write files. It defines source, privacy, provenance, and query boundaries.
2. For a fresh clone, begin with `uv run python scripts/doctor.py --guided`. This is read-only for project data.
3. Work from the requested operating profile. Do not inspect personal `raw/`, `wiki/`, or `episodes/` content merely to explore.

## Choose the operation

- **Setup or health check:** run `doctor.py --guided` first. Use `--fix` only after the user asks to create missing local setup directories or a `sources.yaml` copy.
- **Ingest:** use the existing `scripts/ingest.py` and `commands/ingest.md`. Confirm the exact input and destination before adding data.
- **Curate:** read `commands/curate.md` and preserve raw sources. Treat `--fix`, distillation, lifecycle, reweave, and reconciliation as writes that need the user's requested scope.
- **Query:** read `commands/query.md`; keep it read-only. Answer only from usable trusted claims and state abstention when evidence is absent.
- **Express:** read `commands/express.md`; write output only to the requested output path and distinguish an AI draft from verified source facts.
- **Export:** read `commands/okf.md` and run a dry run before any export. Never use `--share` without an explicit user approval phrase.
- **Wiki web:** `uv run python -m wiki_app` starts the local viewer. Its AI-answer backend is separately configured by `schema/config.yaml` and remains Claude CLI or Anthropic API based.

## Codex interaction

The Codex Desktop app and Codex CLI discover this repo-scoped skill after this repository is opened. Ask in plain Korean, for example:

> `$llm-brain 설치 상태를 읽기 전용으로 점검해줘.`

Do not use Claude Code-only `/llm-brain:...` slash commands in Codex. Translate the requested result into the repository's deterministic script and the applicable command contract instead.

## Completion

Report the exact files changed, whether source data was read or changed, and the command output that verifies the requested result. Never claim that an LLM answer is grounded unless the trusted-claim gate actually passed.
