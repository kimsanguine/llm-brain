---
type: tool
title: Claude Code 에이전트 시스템
description: Claude Code의 .claude/agents/ 폴더에 에이전트를 마크다운으로 정의하면 PM이 팀장처럼 병렬 에이전트 팀을
  운영할 수 있다.
tags:
- claude-code
- multi-agent
- anthropic
timestamp: '2026-05-15'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Claude Code 에이전트 시스템

## 핵심 요약

Claude Code의 `.claude/agents/` 폴더에 에이전트를 마크다운으로 정의하면 PM이 팀장처럼 병렬 에이전트 팀을 운영할 수 있다. 파일 구조가 팀 조직도다.

## 에이전트 정의

```
my-project/
└── .claude/
    └── agents/
        ├── researcher.md
        ├── engineer.md
        └── marketer.md
```

각 파일에 `name`, `description`, `tools` frontmatter + 역할/출력 원칙을 작성한다.

## 서브에이전트 파일 구조 (2026-04-16 추가)

YAML frontmatter 필수 항목: `name`, `description`, `model`, `memory` + 본문(Core Expertise, Principles, Workflow, Quality Bar, Memory 섹션) + 메모리 스캐폴딩.

- `description`의 `<example>` 블록이 자동 위임(delegation) 정확도를 결정 — 3개 이상 권장
- 에이전트 메모리 디렉토리 `~/.claude/agent-memory/<agent>/`는 사전 생성 필수 (첫 호출 시 mkdir 부작용 방지)

## 기존 에이전트 확장 vs 신규 분리 판단 기준

- **통합**: 맥락 공유가 강할 때 (예: Security ↔ Backend 배포)
- **분리**: 레이어가 다를 때 (예: Frontend ↔ Backend)
- 통합 시 반드시 `.bak` 파일 백업 후 덮어쓰기 → `cp .bak` 한 줄로 롤백 가능하게

## 병렬 실행 패턴

```
선형 (기존): 리서치 → 분석 → 문서 → 검토
병렬 (에이전트): 리서치 + 분석 + 문서 + 검토 동시 실행
```

## 활용 원칙

- 에이전트마다 단일 책임 (도메인 분리)
- `isolation: "worktree"` 파라미터로 각 에이전트를 격리 실행 ([steph-ango](/people/steph-ango.md)의 kepano 플러그인 설계 철학처럼, 도구는 하나의 역할에 집중할 때 가장 강력하다)
- 같은 파일 수정하는 작업은 병렬 실행 금지
- 에이전트 정의 전 frontmatter + 핵심 섹션 윤곽을 먼저 사용자에게 승인받을 것
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)의 RLHF 방식처럼 human feedback loop를 에이전트 시스템에 내장할 것 — approval gate 없는 자동화는 도박이다
- fine-tuning 옵션으로 [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md) 패턴을 고려할 수 있지만, 에이전트 레이어에서는 [llm-deployment-patterns](/concepts/llm-deployment-patterns.md) 상의 prompt-based 제어가 우선
- [demis-hassabis](/people/demis-hassabis.md)가 이끈 AlphaCode/AlphaFold 프로세스와 마찬가지로, 도메인 특화 에이전트가 범용 에이전트보다 실제 성과에서 우위

## 관련 개념
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [claude-code-hook-system](/concepts/claude-code-hook-system.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [swe-agent-aci](/tools/swe-agent-aci.md)
- 260515_100_agents
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [steph-ango](/people/steph-ango.md)
- anthropic
- [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md)
- [demis-hassabis](/people/demis-hassabis.md)
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)
