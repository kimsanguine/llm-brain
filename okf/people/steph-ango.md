---
type: person
title: Steph Ango (kepano)
description: Obsidian CEO. "File over app" 철학의 주창자 — 데이터를 plain file로 사용자가 직접 소유하면
  어떤 앱을 쓰든 데이터는 살아남는다.
tags:
- steph-ango
- obsidian
- ceo
- pkm
- file-over-app
timestamp: '2026-05-26'
x-llmbrain-domain:
- knowledge-management
- tools
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://stephango.com
- https://twitter.com/kepano
- https://obsidian.md
- https://github.com/kepano/obsidian-skills
- https://stephango.com/file-over-app (File over app 매니페스토)
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Steph Ango (kepano)

## 핵심 요약

Obsidian CEO. "**File over app**" 철학의 주창자 — 데이터를 plain file로 사용자가 직접 소유하면 어떤 앱을 쓰든 데이터는 살아남는다. 2026-01 **kepano/obsidian-skills** 공개로 Claude Code + Obsidian 통합의 공식 표준을 제시 — 본 wiki에 직접 영향.

## 주요 영향

### 1. "File over app" 매니페스토
- 클라우드 SaaS 노트앱(Notion, Roam 등) 대신 **로컬 markdown 파일**을 표준으로 — [tiago-forte](/people/tiago-forte.md)의 BASB가 SaaS·Notion 중심 생태계를 전제하는 것과 대조적
- 앱은 일시적, 파일은 영구 — 10년 후에도 읽을 수 있는 형식
- 본 wiki의 raw/·wiki/ 모두 plain markdown인 이유의 철학적 출처

### 2. Obsidian 생태계 책임자
- 2021년 Obsidian 합류, 2024년 CEO
- Plugin/Theme/Sync/Publish 통합 생태계 관리
- Graph View, Canvas, Properties, Bases 등 핵심 기능 방향 결정

### 3. kepano/obsidian-skills (2026-01)
Claude Code 공식 Agent Skills로 5개 패키지 공개:
- **obsidian-markdown** — Obsidian Flavored Markdown 규칙
- **obsidian-bases** — `.base` 파일 (database view)
- **json-canvas** — `.canvas` 파일 (JSON Canvas Spec 1.0)
- **obsidian-cli** — `obsidian` CLI 명령
- **defuddle** — 웹 페이지를 깨끗한 markdown으로 정리

본 wiki에서 활발히 사용 중 — `/obsidian-cli` skill 호출, `wiki/canvas/*.canvas` 생성 (json-canvas spec 준수), markdown wikilink 등 모두 이 표준 따름.

## 본 wiki에서의 위치

- [claude-code-agent-system](/tools/claude-code-agent-system.md)의 외부 표준 skills 제공자 (5개 패키지)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)의 vault 시각화(Graph View)를 가능하게 한 도구의 책임자
- Obsidian Canvas (JSON Canvas Spec)가 본 wiki의 `wiki/canvas/ingest-delta.canvas`, `query-*.canvas` 같은 산출물의 표준

## 인용 / 참고할 만한 발언

> "File over app — your tools should respect that your data lives longer than them."

> "Plain text is the only format that has never become obsolete."

## 관련 도구 / 영향력

- 본인 작품: Obsidian (CEO), kepano-obsidian-skills, Minimal Theme (Obsidian 인기 테마)
- 영향받은 진영: Logseq, Roam (반대 진영 SaaS 중심), Notion (반대 진영)

## 관련 개념
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [claude-code](/tools/claude-code.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [tiago-forte](/people/tiago-forte.md) — knowledge management 진영 (Steph: 로컬 파일·Obsidian / Forte: SaaS·Notion 기반)
