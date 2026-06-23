---
type: concept
title: AI 시대 PM 에이전시
description: AI 시대 PM의 차별점은 SQL·Python·LangGraph 같은 개별 스킬 추가가 아니라 에이전시(agency)다.
tags:
- ai-pm
- pm-paradigm
- agency
- decision-making
timestamp: '2026-06-06'
x-llmbrain-domain:
- AI/LLM
- product
- teaching
x-llmbrain-created: '2026-05-18'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# AI 시대 PM 에이전시

## 핵심 요약

AI 시대 PM의 차별점은 SQL·Python·LangGraph 같은 개별 스킬 추가가 아니라 **에이전시(agency)**다. AI가 How 영역의 초안을 빠르게 만들수록 PM의 병목은 무엇을 할지 선택하고, 왜 중요한지 이해하고, 결과 책임을 지는 능력으로 이동한다.

## 작동 원리

### 스킬 희소성의 소멸

raw/blog/2026-05-14 기준, AI는 이미 SQL 작성, 인터뷰 스크립트 초안, A/B 테스트 매트릭스, 경쟁사 분석, 코드베이스 영향범위 평가를 수행한다. PM이 몇 주 배워서 할 수 있는 반복 스킬은 AI가 몇 초 안에 처리하는 영역으로 이동 중이다.

Karpathy의 표현처럼 “vibe coding raises the floor. Agentic engineering raises the ceiling.” 바닥이 올라가면 스킬 자체의 희소성은 줄고, 무엇을 만들지 결정하는 능력이 더 중요해진다.

### 에이전시의 세 요소

- **선택력(Choice)**: 무엇을 할지, 무엇을 하지 않을지 판단한다.
- **주도성(Initiative)**: 지시가 없어도 먼저 문제를 발견하고 움직인다.
- **실행 책임(Accountability)**: AI가 만든 초안이나 분석을 채택한 결정의 결과를 끝까지 소유한다.

핵심 원칙은 Karpathy의 “You can outsource your thinking but you cannot outsource your understanding.” 사고 일부는 위임할 수 있지만, 이해와 책임은 위임할 수 없다.

### 실무에서 보이는 차이

에이전시 없는 PM은 도구 사용법을 묻고, 지시가 있을 때 움직이며, AI 초안을 검토 없이 공유하고, 결과를 클릭률 같은 수치로만 보고한다.

에이전시 있는 PM은 How 이전에 Why를 다시 정의하고, AI 출력물의 가정을 검증하며, “이 정보가 우리 상황에서 의미하는 것”을 직접 해석한다. 이 해석 한 문단이 이해 근육을 유지하는 장치다.

### 2026-06-05 보강: AI 글쓰기 평균화와 목소리의 경쟁우위

The AI Brief raw는 ChatGPT 이후 글쓰기 스타일 다양성이 줄고, AI 작성물이 "LinkedIn average"로 수렴한다는 신호를 정리한다. PM에게 이 문제는 문체 취향이 아니라 에이전시 문제다. AI가 평균적인 전문 문장을 쉽게 만들수록, 차별점은 첫 문장과 마지막 문장, 실제 경험, 구체적 판단, 불완전하지만 살아있는 의견에서 나온다.

실무 원칙은 AI를 작가가 아니라 editor로 쓰는 것이다. 직접 초안을 쓰고 AI에게 명확성·구조·오류 수정만 맡기거나, 자기 글 샘플 3-5개를 먼저 제공해 목소리를 보존한다. 퍼스널 브랜딩에서는 매끄러운 평균보다 "왜 내가 이 말을 하는가"가 더 중요한 신호가 된다.

## 활용 사례

### 에이전트 도입률 5%의 해석

삼성SDS AX센터의 기업 내 에이전트 도입률 5%는 기술 부족보다 **적용 방향을 결정하는 사람의 부족**을 보여준다. 에이전트는 방향이 명확할 때 실행력을 높이지만, 방향이 없으면 복잡한 자동화 스크립트가 된다.

### AI-native PM 팀 비율 변화

Andrew Ng이 말한 엔지니어:PM 비율 8:1 → 1:1 변화는 PM이 더 많은 코드를 직접 써야 한다는 뜻이 아니다. PM 한 명이 더 많은 에이전트를 오케스트레이션하고, 무엇을 만들지·어디서 인간이 개입할지 결정해야 한다는 뜻이다.

## habix/강의와의 연결점

AI PM 교육에서 스킬 체크리스트보다 “판단 구조” 훈련이 먼저다. 수강생에게 AI 출력물을 그대로 제출하게 하기보다, 반드시 “우리 문제에서 이 결과가 의미하는 것”을 한 문단 추가하게 하는 루틴이 에이전시 훈련이 된다.

## 관련 개념

- [ai-pm-role](/concepts/ai-pm-role.md)
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [team-decision-structure-agent-era](/concepts/team-decision-structure-agent-era.md)
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md)
- [agent-build-harness](/insights/agent-build-harness.md)
- [karpathy](/people/karpathy.md) — "vibe coding raises the floor" / "outsource thinking, not understanding" 발언의 출처
- [andrew-ng](/people/andrew-ng.md) — 엔지니어:PM 비율 8:1 → 1:1 전망 발언의 출처
- [claude-code](/tools/claude-code.md) — How 영역 초안 생성의 대표 에이전트 도구
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — 에이전시 없는 PM vs. 에이전시 있는 PM을 가르는 오케스트레이션 구조
- [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md) — 스킬 희소성 소멸의 기술적 배경
