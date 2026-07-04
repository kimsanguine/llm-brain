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
- [ ] `curate_report.md` includes top promote, archive-review, and decay candidates (+ Rescued 섹션). **merge-review 후보 섹션은 v2 deferred** (페이지 유사도 계산 필요 = 범위 밖, Wave3 PM 리뷰).
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

---

# PRD: llm-brain v0.3 — Quality-Driven Curation & Reconciliation (이니셔티브 ③)

> **통합관리 (3축)**: 본 절은 이니셔티브 ③의 요구사항(WHAT) 축. 설계(HOW) = `SPEC.md` "v0.3 Quality-Driven Curation — 설계" 절 · 진행·결정 로그 = `docs/PROGRESS.md` 이니셔티브 ③.
> **출처**: 초안 `~/.openclaw/PRD-llm-brain-v0.3.md` (2026-07-04, 2-에이전트 코드 사실검증·설계 크로스체크 후 개정 이관 — 개정 7건은 PROGRESS Decision Log ③).
> **대상 버전**: v0.2.0(Agent Memory OS) → v0.3.0 / v0.3.1 / v0.3.2

## Problem Statement

`curate --distill`은 길이 압축(access 기반 3분류 큐)에 가깝고, 여러 raw 소스에 걸친 교차 종합·판단 추출이 약하다. 승격/유지가 품질이 아니라 시간(TTL·주 1회 월요일 distill)으로 굴러가고, 중복은 경고만 하고 저장을 강행하며(`is_duplicate()` soft — 저장 완료 후 호출이라 구조적으로 차단 불가), 새 소스가 기존 wiki와 모순될 때 화해 로직이 없다(`run_audit`의 `contradictions=[]` stub). 결과: 지식은 쌓이지만 "믿고 꺼내 쓸 판단"으로 익지 않고, Express 초안 품질이 정체된다.

## Goals

| # | 목표 | 성공 기준 | 측정 |
|---|---|---|---|
| G1 | distill이 교차 종합을 산출 | 대상 페이지 ≥70%에 2+ 소스 교차 인용 `## 인사이트 (종합)` 생성 | `curate_report.md` synthesis 카운트 |
| G2 | 승격이 Promotion Gates(G-1~G-4)를 통과해야만 발생 | 신규 페이지 100% 게이트 통과 로그, 미달은 observing/rejected 라우팅 | gate 결정 로그 |
| G3 | 유지가 매일 품질 기반으로 동작 | weak-node(본문<800자 OR 근거<2건 OR H2<3개) 잔여 주간 0 수렴 | `memory_health_report.md` 추이 |
| G4 | 중복·저가치 raw 입구 차단 | hard-block 후 wiki 중복 신규 생성 0건/주 | 중복 slug 충돌 로그 |
| G5 | 모순의 명시적 화해 | 모순 감지 시 100%가 `## 반론/갱신` + superseded 표시 동반 | reconciliation 이벤트 |

상위 제품 가설: G1~G5 충족 시 Express output-ready 비율 상승 (별도 실험 검증).

## 핵심 설계 원칙 — v0.2.0 계약 준수 (검토 개정의 본체)

1. **LLM 실행 경계 유지**: `scripts/`는 결정적 스캐너·큐 생성까지만 (synthesis 대상 선정·모순 후보 탐지 → `reweave_queue.md`·`contradiction_queue.md`). 생성 작업(종합 작성·화해 서술)은 `commands/curate.md`의 Step으로 Claude Code가 수행. "claude CLI 없이 pytest 통과" 계약 불변.
2. **자동 병합 금지 (Rule 9, v0.2.0 확정 결정 유지)**: hard dedup의 범위는 "저장 차단 + 기존 페이지 강화 라우팅 제안"까지. 병합 실행은 사람/컴파일러 결정.
3. **`wiki/observing/`·`wiki/rejected/` 신설 = 3점 방어 동반 (one-way door)**: `schema/okf_export.yaml` exclude_paths + `curate.find_all_wiki_pages` 제외 + lifecycle 제외를 폴더 신설과 같은 커밋에. 두 폴더는 episodes와 동일하게 gitignore.
4. **raw write = body 무손상**: 기존 `frontmatter_utils.read_fm/write_fm`으로 충족 (fm 블록 yaml 재직렬화는 허용, 본문 바이트 보존). 파서 5번째 신설 금지 — `frontmatter_utils`로 수렴.
5. **기존 엔진 재사용 (v0.2 PRD Technical Consideration 준수)**: reweave는 신규 엔진이 아니라 `run_distill`+`run_lifecycle`+`find_merge_candidates` 오케스트레이터. 유사도는 기존 `_merge_token_set` Jaccard 재사용.
6. **불변식**: 본문·`sources` 단축/삭제 금지(append/갱신만, shrink 가드) · 자동 fix는 idempotent · wiki 수정은 raw 출처 필수 · `--dry-run` 우선.

## 워크스트림 (WS-1~6)

### WS-1 · Synthesis Distill (v0.3.1)
- **P0**: 페이지별 `## 인사이트 (종합)` — 2+ raw 교차 인용, 강한 각도 1~3개, 반복 신호 카운트. 기존 본문 append/갱신만.
- **P0**: `distill_level` 상승해도 근거 수 유지·증가 (shrink 시 저장 거부 + `WARN shrink`).
- **P1**: 교차도 가중(inbound 허브 우선). **P2**: 각도→Express 훅 매핑.
- 설계: 결정적 대상 선정은 `curate.py`(큐), 생성 규칙은 `schema/curate.md` `## Synthesis Rules`(기존 "3+ 페이지 → insights/" 규칙의 확장), 실행은 `commands/curate.md` Step. frontmatter: `angles`, `signal_count`, `synthesis_updated`.

### WS-2 · Promotion Gates G-1~G-4 (v0.3.0)
- **P0 G-1 신규 생성**: 반복 ≥2회(7일)·본문 ≥800자·H2 ≥3개·근거 ≥2건·frontmatter 완비·summary 40~200자·기존 유사도 <0.75 전부 충족 시만 생성.
- **P0 G-2 기존 강화**: 사례 ≥1건 OR 새 각도 ≥200자, 강화 후 본문 ≥800자 유지.
- **P0 G-3 기각 라우팅**: 사유 분류(`low_value`/`insufficient_recurrence`/`insufficient_content`/`duplicate_existing`/`frontmatter_invalid`) → `wiki/rejected/`.
- **P0 G-4 observing**: 반복 1회 잠재가치 → `wiki/observing/` 7일 유예(`observation_expires`), 재등장 시 승격.
- **P1**: 전 결정 `curate_report.md` 로깅.
- 설계: `scripts/lib/memory_score.py` 추출(선행) → `scripts/lib/gates.py` `evaluate_promotion(candidate) -> Decision`. frontmatter: `gate_status`(episodes의 `status`와 의미 충돌 회피 개명), `observation_expires`, `recurrence`. 용어: 기존 "Quality Gates"(CI 명령)와 구분해 **Promotion Gates**로 통일.

### WS-3 · Daily Quality-Driven Curate (v0.3.0)
- **P0**: `curate --reweave` — weak-node 전수 스캔, 자동 보강 가능분(frontmatter·summary 결손)은 즉시 fix, 판단 필요분(본문·근거 부족)은 alert (가짜 보강 금지).
- **P0**: `run_daily.sh`에 매일 Step으로 추가 (월요일 distill과 별개).
- **P1**: 일요일 `--weekly-summary`(4주 누적 weak → 통합/삭제 후보) · `--fix`/`--dry-run` · idempotent.
- 설계: reweave = 기존 3함수 오케스트레이터 + weak 신규 기준(800자/근거 2건/H2 3개 — 현 memory_health의 orphan·confidence·stale 기준에 추가). `memory_health.py`에 `--fix`. episode 기록은 `_record_curate_episode` 패턴 + `task_type: reweave`(memory_score `episode_ref` 집계 제외 규칙 동반).

### WS-4 · Hard Dedup + Capture Filter (v0.3.0)
- **P0**: dedup hard-block — `is_duplicate` 호출을 **저장 전으로 재배선**(현재는 저장 후 호출) + 반환 `(is_dup, target_slug, score)` 확장. 기본 저장 보류 + 강화 라우팅 제안, `--force`로만 강행.
- **P0**: capture 필터 — `require_keywords`·`min_word_count` 실구현 (현재 SPEC.md 표에만 예약, `sources.yaml`·`sync_raw.py` 미배선).
- **P1**: 유사도 dedup(슬러그 → 슬러그+키워드 Jaccard, 기존 `_merge_token_set` 재사용).

### WS-5 · Contradiction Reconciliation (v0.3.1)
- **P0**: 신규 근거가 기존 주장과 상충 시 `## 반론/갱신 (YYYY-MM-DD)` append — 기존 주장/반례 근거/현재 판단. 삭제 금지, 옛 주장 superseded 표시(frontmatter `superseded_claims`).
- **P1**: query 응답 시 최신 판단 우선 + 갱신 맥락 유지.
- 설계: `run_audit`의 `contradictions=[]` stub + `schema/curate.md` 모순 리포트 섹션(기예약)을 채우는 형태. 결정적 후보 탐지는 스크립트, 화해 서술은 커맨드 Step. 오탐 방지: 모순 없는 보강 raw에는 반론 섹션 미생성.

### WS-6 · Engine 완성 + Team-Ready 훅 (v0.3.2)
- **P0**: `scripts/lib/llm_client.py` — SPEC "LLM 엔진 통합" 예약 인터페이스(`engine: cli|api`) 구현. 기존 유일 호출부 `wiki_app/api.py`의 subprocess 2곳도 이 클라이언트로 통합.
- **P1**: `owner`/`scope: private|shared` frontmatter + okf scope 필터. **P2**: 다중 기여자 병합 예약.

## Non-Goals

멀티유저 실시간 협업 · 임베딩/벡터DB(유사도는 경량 Jaccard) · wiki_app UI 개편(새 필드 표시만) · 실시간 재컴파일 · distill 프롬프트 자동 튜닝 · 메모리 자동 삭제(v0.2 계승) · 자동 병합.

## Phasing

| 릴리스 | 범위 | 성격 |
|---|---|---|
| **v0.3.0 Depth Core** | WS-2(게이트)+WS-3(reweave)+WS-4(dedup) + 선행(안전망 테스트·`run_daily.sh` 경로 drift 수정·memory_score lib 추출) | 품질로 승격·유지·차단하는 뼈대 |
| **v0.3.1 Synthesis** | WS-1(종합)+WS-5(화해) | 판단 종합의 살 — 게이트 위에 얹어야 안전 |
| **v0.3.2 Engine** | WS-6 | 엔진 통일 + 팀 훅 |

## Success Metrics

- Leading(1~2주): synthesis 커버리지 ≥70% · 게이트 통과 로그 100% · weak 잔여 4주 내 0 수렴 · 중복 신규 0건/주.
- Lagging(4~8주): Express output-ready 비율 상승(수동 라벨) · shrink 사건 0건 · 화해 이벤트 100% 형식 준수.
- 측정: 전부 파일 산출물 파싱 (`curate_report.md`·`memory_health_report.md`·frontmatter). 텔레메트리 불필요.

## 확정 결정 (2026-07-04 — 상세 PROGRESS Decision Log ③)

LLM 경계=큐+커맨드 분리 · observing/rejected=gitignore+3점 방어 · raw write=body 무손상(기존 유틸 충족) · hard dedup=차단+라우팅까지(자동 병합 금지).

## Open Questions (잔여)

- Q1: 유사도 임계 0.75/0.85 캘리브레이션 — 초기값 시작 후 튜닝 (비블로킹).
- Q3: 모순 감지 재현율/정밀도 — 임계 보수적 시작, 오탐(반론 남발) 모니터 (비블로킹).
- Q4: api 모드 시 reweave·distill 토큰 예산 (비블로킹, v0.3.2 전 결정).
- Q5: 종합 프롬프트 — OpenClaw `SOURCE-TO-TOPIC-RULES` 이식 vs llm-brain 톤 재작성 (v0.3.1 착수 시 결정).
