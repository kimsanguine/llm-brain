---
type: person
title: Tiago Forte
description: 생산성 컨설턴트, Forte Labs 창립자.
tags:
- tiago-forte
- second-brain
- pkm
- ai-educator
- forte-labs
timestamp: '2026-05-26'
x-llmbrain-domain:
- knowledge-management
- productivity
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://fortelabs.com
- Building a Second Brain (Atria Books, 2022)
- https://fortelabs.com/blog/basboverview/
- https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Tiago Forte

## 핵심 요약

생산성 컨설턴트, Forte Labs 창립자. "Building a Second Brain (BASB)" 저자. 디지털 정보 과부하 시대에 **CODE 프레임워크 (Capture · Organize · Distill · Express)** 와 **Progressive Summarization (점진적 압축)** 방법론을 제시. 본 wiki의 distill·express 사이클의 직접 출처.

## 주요 영향

### 1. CODE 프레임워크 (지식 생애주기)

```
C apture  →  O rganize  →  D istill  →  E xpress
  수집           정리          정제          출력
```

- **Capture**: 관심을 끄는 모든 것 수집 (resonance 기반)
- **Organize**: 행동에 따라 정리 (PARA: Projects/Areas/Resources/Archive)
- **Distill**: 핵심만 추출 (Progressive Summarization 4단계)
- **Express**: 자기 글·작품으로 출력 — "뇌는 아이디어를 떠올리는 곳이지 저장하는 곳이 아니다"

### 2. Progressive Summarization (점진적 압축)

원문 → bold 강조 → highlight → 한 줄 요약. 자주 보는 노트일수록 더 깊이 압축. 본 wiki의 `distill_level: 0→1→2→3` 단계가 이 방법론의 LLM 자동화 버전.

### 3. "Express가 진짜 목적이다"

지식을 쌓기만 하는 노트 시스템의 한계 지적. Second Brain은 결국 **출력 (글, 발표, 작품)** 을 만들기 위해 존재. 본 wiki의 `express/` 카테고리 (blog/lecture/summary/report)가 이 정신의 직접 구현.

## 본 wiki에서의 위치

- [260515_llm_wiki](/projects/260515_llm_wiki.md)의 **distill·express 사이클 출처** — [karpathy](/people/karpathy.md)가 raw→wiki 컴파일을 제시했다면, Forte는 그 wiki를 어떻게 압축·출력할지 답함
- habix-profile의 **"Context Dealer" 포지셔닝**도 Forte의 "Distill을 사람이 직접 vs 자동화"에서 한 발 더 나아간 형태 — distill은 LLM에 위임, 사람은 Express에만 집중
- [ai-pm-role](/concepts/ai-pm-role.md)의 "PM이 무엇을 만들지 결정"이라는 명제도 Forte의 Express 우선 정신과 같은 축

## 인용 / 참고할 만한 발언

> "Your brain is for having ideas, not storing them."

> "Knowledge management is not about preserving information, but about transforming it."

## 한계 / 비판 영역

- BASB는 1인 운영자 관점 — 팀/조직 차원 협업은 약함
- Progressive Summarization은 LLM 자동화 등장 이전 시대의 방법 — 본 wiki의 `curate --distill` LLM 위임이 한 단계 진화

## 관련 개념

- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- habix-profile
- [ai-pm-role](/concepts/ai-pm-role.md)
- [karpathy](/people/karpathy.md) — LLM Wiki 패턴 원조 (Forte의 distill 위임 정신을 LLM으로 자동화하는 진영의 출발점)
- [steph-ango](/people/steph-ango.md) — knowledge management 도구 진영의 다른 축 (Forte: SaaS·Notion 기반 / Steph: 로컬 파일·Obsidian 기반)
