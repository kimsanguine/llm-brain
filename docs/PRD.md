[PRD]
# PRD: llm-brain Agent Memory OS Upgrade

> **통합관리 (3축)**: 본 문서는 요구사항(WHAT) 축. 설계(HOW) = `SPEC.md` "Agent Memory OS Upgrade — 설계" 절 · 진행·결정 로그 = `docs/PROGRESS.md` 이니셔티브 ②. (Desktop `~/Desktop/prd.md`에서 2026-06-27 이관.)
> **확정 결정** (Open Questions 일부 해소): memory_score = 재사용 우선 · resonance v1 제외 · episodes 월별 샤드 + 전체 gitignore · episodes/·procedures/ repo 루트 격리. 상세 = PROGRESS Decision Log ②.

## Overview

`llm-brain` is currently strong as a file-based Second Brain Compiler: it turns `raw/` sources into structured `wiki/` pages, supports `express/` outputs, and exports an OKF-compatible bundle.

The next product step is to upgrade it from a knowledge compiler into an agent memory operating layer. Based on the 5-layer agent memory model, this PRD focuses on adding explicit support for:

- Working memory: task-specific context packs for the current run.
- Episodic memory: structured execution history.
- Semantic memory: existing `wiki/` pages, with clearer memory metadata.
- Procedural memory: reusable procedures/playbooks separated from general docs.
- Meta memory: scoring and lifecycle control for promote/merge/archive/decay decisions.

The guiding principle is to preserve the current markdown-first philosophy. This is not a vector database rewrite and not a generic RAG product.

## Background and Context

This PRD comes from a broader product thesis: agent memory is often misunderstood as a storage problem, but in real agent operation it behaves more like an operating layer.

In the current AI product market, many memory implementations focus on saving chat history, embedding documents, or retrieving semantically similar chunks. That is useful, but insufficient for long-running agents. Agents fail not only because they lack memory, but because they read the wrong memory, duplicate stale memory, forget important operational decisions, or cannot distinguish facts from procedures.

The recent LinkedIn post on AI agent memory framed this as a 5-layer structure:

1. Working memory: the current turn, goal, plan, intermediate state, and active context.
2. Episodic memory: what happened, when it happened, which sources were used, and what outcome followed.
3. Semantic memory: durable facts about users, projects, concepts, tools, people, policies, and preferences.
4. Procedural memory: reusable workflows, playbooks, commands, and skills for doing work.
5. Meta memory: the control plane that decides what to keep, merge, promote, archive, decay, or forget.

`llm-brain` already has a strong foundation for semantic memory. Its `raw/ -> wiki/ -> express/ -> okf/` pipeline embodies the idea that LLMs can act as compilers over personal knowledge. It also aligns with the markdown-first philosophy: keep knowledge inspectable, editable, linkable, and portable.

However, if `llm-brain` is going to support agentic workflows, content production, teaching material reuse, and future 100 Agents-style operating systems, it needs to represent more than static knowledge pages. It needs to remember runs, decisions, outputs, procedures, and memory-management policies.

This upgrade should therefore be understood as a product transition:

```text
Current llm-brain:
raw sources -> structured wiki -> searchable/expressable knowledge

Target llm-brain:
raw sources + runs + procedures + curation policy
  -> agent-ready memory operating layer
  -> compact context packs, reusable episodes, and governed long-term memory
```

The goal is not to make `llm-brain` a generic RAG system. The goal is to make it a practical, file-based memory OS for agents: a system that knows what to read, what to remember, what to reuse, and what to safely forget.

This matters for Ethan's broader work because `llm-brain` can become a concrete reference implementation for the argument that "memory is not a feature; it is part of the agent operating system." It can also become reusable infrastructure for OpenClaw, 100 Agents, LinkedIn content workflows, lecture preparation, and project knowledge management.

The product posture should remain opinionated:

- Prefer structured markdown and JSONL over hidden databases.
- Prefer source-grounded wiki pages over hallucinated summaries.
- Prefer explicit procedures over implicit prompt habits.
- Prefer curated memory over unlimited accumulation.
- Prefer inspectable agent context packs over opaque retrieval.

## Goals

- Make every meaningful agent run reusable as structured episodic memory.
- Generate compact working-memory packs before query, express, or future agent tasks.
- Add memory classification metadata without breaking existing wiki pages.
- Improve `curate` from access-count-based distillation into meta-memory prioritization.
- Keep all memory artifacts file-based, inspectable, git-friendly, and safe for public/private separation.
- Preserve current `raw/` provenance guardrails: no wiki fact without source.

## Quality Gates

These commands must pass for every user story:

- `uv run pytest` - full Python test suite.
- `uv run python scripts/curate.py --audit` - basic wiki audit must run without crashing on existing data.

For stories that change export behavior:

- `uv run python scripts/okf_export.py --dry-run` - OKF export dry run must complete.

For stories that change web behavior:

- `uv run python -m wiki_app` should start successfully.
- Existing `tests/test_wiki_app_*.py` must pass.

## User Stories

### US-001: Add Episodic Memory Ledger

**Description:** As an llm-brain user, I want every meaningful run to be saved as structured episodic memory so that future agents can reuse past work, decisions, sources, and outcomes.

**Acceptance Criteria:**

- [ ] Add an `episodes/` directory that is safe for private/local use and can be gitignored by default if needed.
- [ ] Add `scripts/episode.py` with append/read helpers for JSONL episode records.
- [ ] Episode records include at minimum: `timestamp`, `task_type`, `user_goal`, `inputs`, `read_pages`, `procedures_used`, `outputs`, `status`, and `notes`.
- [ ] Episode write is append-only and does not modify existing episode records.
- [ ] Add tests covering valid append, malformed input rejection, and reading recent episodes.
- [ ] Document the episode schema in `SPEC.md`.

### US-002: Record Episodes from Existing Commands

**Description:** As an llm-brain user, I want `ingest`, `curate`, `express`, and wiki AI answer flows to write episode summaries so that operational history is captured automatically.

**Acceptance Criteria:**

- [ ] `scripts/ingest.py` records an episode when URL/file/note ingestion succeeds.
- [ ] `scripts/curate.py` records an episode summarizing audit, distill candidates, lifecycle candidates, and graph health when applicable.
- [ ] `scripts/express.py` records an episode with topic, output path, source pages, and output type.
- [ ] `wiki_app/api.py` records an episode for AI answer requests with question, selected context slugs, valid sources, and status.
- [ ] Episode recording failures do not break the main command path; they warn and continue.
- [ ] Tests verify episode records are produced without requiring Claude CLI.

### US-003: Add Memory Type Metadata

**Description:** As an llm-brain user, I want wiki pages and procedures to declare their memory role so that agents can distinguish semantic facts from procedures, episodes, and meta rules.

**Acceptance Criteria:**

- [ ] Define supported `memory_type` values: `semantic`, `episodic`, `procedural`, `meta`, and `working`.
- [ ] Add optional frontmatter fields: `memory_type`, `retention`, `confidence`, `source_count`, `last_verified`, and `decay_policy`.
- [ ] Existing wiki pages remain valid if these fields are absent.
- [ ] `curate` can read the new fields without rewriting unrelated metadata.
- [ ] `okf_export.py` preserves internal memory fields as `x-llmbrain-*` unless `--strip-internal` is used.
- [ ] Add schema documentation to `SPEC.md` and `README.md`.

### US-004: Introduce Procedural Memory Directory

**Description:** As an llm-brain user, I want procedures and reusable workflows separated from semantic wiki pages so that agents can reliably load "how to do work" instructions.

**Acceptance Criteria:**

- [ ] Add a `procedures/` directory for reusable workflows.
- [ ] Add example procedures for `ingest`, `curate`, `express-blog`, and `okf-export-safety`.
- [ ] Procedure files use frontmatter with `memory_type: procedural`.
- [ ] Add a loader helper that can list and read procedure files by slug.
- [ ] Existing `schema/*.md` files are not deleted; they may link to equivalent procedures.
- [ ] Document how procedures differ from wiki semantic pages.

### US-005: Build Working Memory Pack Generator

**Description:** As an agent using llm-brain, I want a compact context pack for a task so that I can reason with the right semantic pages, recent episodes, and relevant procedures without loading the whole wiki.

**Acceptance Criteria:**

- [ ] Add `scripts/brain_context.py`.
- [ ] CLI supports `--task`, `--topic`, `--type query|express|curate|custom`, and `--max-pages`.
- [ ] Output is markdown by default and JSON with `--json`.
- [ ] The pack includes: current goal, related semantic pages, recent related episodes, candidate procedures, constraints, and source paths.
- [ ] Page selection initially uses existing index keyword matching plus graph degree as tie-breaker.
- [ ] Episode selection uses recent episodes filtered by task type/topic keyword.
- [ ] The generated pack has deterministic ordering for testability.
- [ ] Add tests for empty wiki, matching wiki pages, related episodes, and procedure inclusion.

### US-006: Upgrade Curate into Meta Memory Scoring

**Description:** As an llm-brain user, I want `curate` to prioritize memories based on operational value, not only access count, so that important but less-clicked knowledge is not lost.

**Acceptance Criteria:**

- [ ] Add a `memory_score` calculation for wiki pages.
- [ ] Score inputs include at minimum: `resonance`, `access_count`, recency, graph centrality/degree, source count, express reuse, stale age, and contradiction risk placeholder.
- [ ] `curate --distill` writes score reasons into `wiki/distill_queue.md`.
- [ ] `curate_report.md` includes top promote, merge-review, archive-review, and decay candidates.
- [ ] Score calculation is deterministic and covered by unit tests.
- [ ] Existing access-count thresholds remain supported as a backward-compatible fallback.

### US-007: Track Express Output Reuse

**Description:** As an llm-brain user, I want outputs such as blog drafts, LinkedIn posts, lectures, and reports to feed back into memory with outcome metadata so that high-value patterns become reusable.

**Acceptance Criteria:**

- [ ] Express output frontmatter supports `output_type`, `status`, `published_url`, `source_pages`, `derived_insight`, and `reuse_as`.
- [ ] `scripts/express.py` writes source pages in a machine-readable YAML list.
- [ ] Blog outputs copied to `raw/blog/` retain enough metadata for future ingest.
- [ ] Episode records include express output paths and source pages.
- [ ] Add tests for generated express frontmatter.

### US-008: Add Memory Health Report

**Description:** As an llm-brain user, I want a memory health report so that I can see whether the system is accumulating useful memory or just collecting files.

**Acceptance Criteria:**

- [ ] Add `scripts/memory_health.py` or extend `curate --health`.
- [ ] Report includes counts by memory type, orphan semantic pages, stale procedures, recent episodes, top reused pages, low-confidence pages, and archive candidates.
- [ ] Report writes to `wiki/memory_health_report.md`.
- [ ] Report is read-only and never moves/deletes files.
- [ ] Add tests for report generation on fixtures.

## Functional Requirements

- FR-1: The system must store episodic records as JSONL files under `episodes/`.
- FR-2: The system must support explicit memory classification through `memory_type`.
- FR-3: The system must preserve current `raw/` source provenance rules.
- FR-4: The system must generate a task-specific working memory pack without requiring a vector database.
- FR-5: The system must select relevant context from wiki pages, episodes, and procedures.
- FR-6: The system must compute deterministic meta-memory scores for curation.
- FR-7: The system must keep all new artifacts inspectable as markdown, YAML, or JSONL.
- FR-8: The system must fail soft for episode logging and fail loud for data loss or unsafe export risks.
- FR-9: The system must remain compatible with existing `wiki_app`, `okf_export`, and test fixtures.
- FR-10: The system must document all new file formats and commands.

## Non-Goals

- Do not introduce a vector database in this phase.
- Do not replace the current `raw/ → wiki/` compiler model.
- Do not auto-delete memories.
- Do not publish private episodes or procedures through OKF by default.
- Do not require a hosted backend or external database.
- Do not build a full multi-agent orchestration platform in this phase.
- Do not rewrite the existing web UI unless required for health/report visibility.

## Technical Considerations

- Existing code is Python 3.11+ with `uv`, FastAPI, markdown/frontmatter utilities, and pytest.
- Existing privacy boundary matters because the repo is public while real `raw/`, `wiki/`, and local config can be private.
- `episodes/` may contain sensitive operational context. Default should be private/local-first.
- `okf_export.py` must not leak private local memory fields or episode contents unless explicitly configured.
- Existing `curate.py` already has access tracking, lifecycle, graph health, and distill queue logic. Reuse these patterns rather than creating a separate curation engine.
- Existing `express.py` has related-page collection based on index keyword matching. `brain_context.py` can start from this and later evolve into hybrid retrieval.
- `wiki_app/api.py` has token and timeout safeguards for Claude CLI calls. Any working-memory integration should keep context caps.

## Suggested Implementation Order

1. Add `episodes/` schema and `scripts/episode.py`.
2. Add tests for episode append/read.
3. Wire episode recording into `express.py` first because it is low-risk and high-value.
4. Add `memory_type` metadata documentation and reader support.
5. Add `procedures/` and procedure loader.
6. Build `scripts/brain_context.py`.
7. Extend `curate.py` with `memory_score`.
8. Add memory health report.
9. Update README/SPEC/CLAUDE docs.

## Success Metrics

- A future agent can answer "what did I do last time on this topic?" from episode records.
- `brain_context.py` produces a useful task pack in under one second on the current repo size.
- `curate --distill` explains why each memory is prioritized, not just its access count.
- New metadata does not break current wiki pages or OKF export.
- Full test suite passes after each story.
- The system remains file-first and easy to inspect manually.

## Open Questions

- ~~Should `episodes/` be committed for demo data only, while real local episodes stay gitignored?~~ → **해소(2026-06-27):** `episodes/` 전체 gitignore + `examples/episode-schema-example.jsonl` 1개만 커밋(문서·테스트용). 월별 샤드 `episodes/YYYY-MM.jsonl`.
- Should LinkedIn publishing outcomes be captured directly in llm-brain, or should that remain in OpenClaw memory and only selected outcomes be imported?
- Should `procedures/` eventually become a Codex/OpenClaw skill export format?
- Should `brain_context.py` later support embeddings as an optional adapter, while keeping file-first retrieval as default?
- Should memory health be exposed in `wiki_app` UI after CLI reporting is stable?

[/PRD]
