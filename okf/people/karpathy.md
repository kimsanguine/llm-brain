---
type: person
title: Andrej Karpathy
description: '"LLM을 컴파일러처럼 써라.'
tags:
- karpathy
- openai-alumni
- founder
- ai-educator
- deep-learning
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- knowledge-management
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://karpathy.ai
- https://twitter.com/karpathy
- https://x.com/karpathy/status/llm-wiki-tweet (LLM Wiki 패턴 원본 트윗)
- 'https://www.youtube.com/@AndrejKarpathy (Neural Networks: Zero to Hero)'
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Andrej Karpathy

## 핵심 요약

전 Tesla AI Director, 전 OpenAI 창립 멤버. 2024년 OpenAI를 떠난 후 AI 교육·YouTube 강의(Neural Networks: Zero to Hero)와 GitHub micrograd·nanoGPT·llm.c 같은 reference 구현으로 LLM 교육 표준을 만들었다. 본 wiki의 **LLM Wiki 패턴**(raw → 컴파일 → wiki) 원조. 같은 OpenAI 창립 세대에서 독립한 [mira-murati](/people/mira-murati.md)와 대조적 행보(교육·연구 vs 새 frontier lab)를 보인다.

## 주요 영향

### 1. LLM Wiki 패턴 (본 시스템 출발점)
Karpathy가 트위터에서 제시한 "LLM을 컴파일러처럼 써라. raw 메모를 넣으면 구조화된 위키가 나온다"가 [260515_llm_wiki](/projects/260515_llm_wiki.md) 프로젝트의 핵심 아이디어. raw/ → wiki/ 2계층 + LLM 컴파일러 구조의 직접 출처. [tiago-forte](/people/tiago-forte.md)의 Second Brain(distill·express 사이클)을 LLM으로 자동화하는 방향의 출발점이기도 하다.

### 2. AI 교육의 표준화
- **Neural Networks: Zero to Hero** YouTube 시리즈 — backprop부터 GPT까지 hands-on
- **nanoGPT**: GPT-2 재현 minimal 코드 (~300 lines)
- **llm.c**: pure C로 GPT 학습 — frameworks 의존 제거
- **micrograd**: backprop을 100줄로 — 교육용 최소 구현

### 3. 1인 풀스택 reference 구현 패턴
한 사람이 데이터 수집 → 학습 → 평가 → 배포까지 minimal하게 보여주는 코드 스타일이 본 wiki의 "1인 운영 AI 시스템" 구조에 영향. [claude-code-agent-system](/tools/claude-code-agent-system.md)의 단일 사용자 + 에이전트 팀 패턴도 같은 정신.

## 본 wiki에서의 위치

- [260515_llm_wiki](/projects/260515_llm_wiki.md) 의 원형 아이디어 제공자
- [claude-code](/tools/claude-code.md) CLI는 Karpathy 스타일 "minimal reference"가 production 도구로 진화한 사례
- [ai-pm-role](/concepts/ai-pm-role.md)의 "코드 자동화 시대 인간의 역할" 논의와 그의 minimal 교육 코드 철학은 같은 축

## 인용 / 참고할 만한 발언

> "LLM을 컴파일러처럼 써라. raw 메모를 넣으면 구조화된 위키가 나온다."

> "Software 1.0 = manual code. Software 2.0 = neural networks. Software 3.0 = prompts."

## 관련 개념
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [claude-code](/tools/claude-code.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [mira-murati](/people/mira-murati.md) — OpenAI 동시대 (창립 멤버) 후 독립한 frontier lab founder 패턴 동료
- [tiago-forte](/people/tiago-forte.md) — Forte Second Brain의 distill 위임 정신을 LLM으로 자동화하는 진영의 출발점
