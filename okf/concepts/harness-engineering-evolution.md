---
type: concept
title: 하네스 엔지니어링 3세대 진화
description: '핵심 질문: "무슨 말을 해야 하나?"'
tags:
- harness
- harness-engineering
- prompt-engineering
- context-engineering
timestamp: '2026-06-14'
x-llmbrain-domain: AI/LLM
x-llmbrain-created: '2026-05-16'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 하네스 엔지니어링 3세대 진화

## 핵심 요약

2022-2026 AI 개발 패러다임이 3번 이동했다: 프롬프트 엔지니어링(무슨 말을 할까) → 컨텍스트 엔지니어링(무슨 정보를 줄까) → 하네스 엔지니어링(어떤 시스템을 만들까). Chad Fowler의 원칙 "엄격함은 사라지지 않았다. 위치가 바뀌었을 뿐"이 이 전환을 설명한다.

## 작동 원리

### 1세대: Prompt Engineering (2022-2024)

**핵심 질문**: "무슨 말을 해야 하나?"

Chain-of-Thought, ReAct 등 추론 기법이 출력 품질을 극적으로 향상시켰다. 그러나 에이전트가 접근할 수 없는 정보는 프롬프트로 해결할 수 없었고, 측정 없는 맹목적 프롬프팅으로 붕괴했다.

2026-06-12~13 AI Human Ch07 브리프는 이 전환을 강의 맥락에서도 재확인한다. 보리스 체르니의 자율 루프, 아사나 공유 메모리, OpenAI Lockdown Mode, Microsoft Agent 365, Anthropic Agent Skills는 프롬프트가 사라지는 것이 아니라 루프·메모리·권한·평가 체계 안으로 흡수된다는 신호다. 상세 정리는 [prompt-engineering-as-system-design](/concepts/prompt-engineering-as-system-design.md) 참조.

### 2세대: Context Engineering (2025)

**핵심 질문**: "어떤 정보를 제공해야 하나?"

핵심 지표: KV-cache hit rate — 프리픽스 안정성이 비용을 **10배 절감**.
4가지 전략: Write / Select / Compress / Isolate.
도구: RAG 파이프라인, MCP (Model Context Protocol).

그러나 완벽한 컨텍스트도 잘못 설계된 시스템에서는 실패한다.

### 3세대: Harness Engineering (2026+)

**핵심 질문**: "어떤 시스템을 만들어야 하나?"

Mitchell Hashimoto 원칙: "에이전트가 실수할 때마다, 그 실수가 구조적으로 재발하지 않도록 시스템을 변경하라."

결정론적 강제 > 확률론적 유도. 프롬프트로 코딩 표준을 지키라고 요청하면 확률론적으로 준수하지만, linter가 위반을 차단하면 결정론적으로 강제된다.

---

## 패러다임 전환의 증거 (수치)

| 지표 | 데이터 | 출처 |
|---|---|---|
| 엔터프라이즈 AI 프로덕션 실패율 | 최대 88% | Medium/Adnan Masood |
| 실패 원인 중 하네스 결함 | 65% | Medium/Adnan Masood |
| Vercel 툴 최적화 정확도 향상 | 80% → 100% | DEV Community |
| APEX-Agents 실제 전문 작업 통과율 | ~24% (첫 시도) | DEV Community |
| 하네스 최적화 토큰 비용 절감 | $3.00 → $0.30/MTok | Medium/Adnan Masood |
| OpenAI Codex 팀 생산성 | 3.5 PR/인/일 (3명 엔지니어) | Evolution post |

---

## 활용 사례

**Anthropic 3-에이전트 하네스**: Planner + Generator + Evaluator 분리로 Opus 4.5에서 4시간 세션 지속 가능.
Opus 4.6 이후 하네스 단순화 → 3.8시간 + $124.70으로 DAW 프로젝트 완성.

**OpenAI Codex**: 레포지토리 지식 체계화 + 기계적 룰 강제 + 점진적 컨텍스트 공개로 100만 줄 코드 생성.

**Ralph 패턴**: 컨텍스트 윈도우 대신 git 히스토리와 파일로 상태 유지 → 야간 자율 에이전트 실행.

---

## habix/강의와의 연결점

**habix**: CLAUDE.md + hooks + eval.sh 구조가 바로 하네스 엔지니어링의 실제 적용. "모델이 병목이 아니다"라는 관점은 Codex CLI 선택 기준에도 직접 적용됨.

**강의**: AI Human 수강생들에게 "프롬프트 잘 짜는 법"보다 "하네스 잘 만드는 법"이 더 중요한 스킬임을 이 3세대 진화로 설명 가능. 2세대 → 3세대 전환이 현재 진행 중인 변화여서 체감이 쉬움.

## 보안 주의점

Simon Willison의 **Lethal Trifecta**: 신뢰할 수 없는 입력 + 민감 데이터 접근 + 상태 수정 권한을 **동시에** 가진 에이전트는 구조적 취약점.

## 관련 개념

- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — 하네스의 구체적 설계 패턴 (OpenAI/Anthropic 프레임워크)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) — 3세대 핵심 패턴: Planner-Generator-Evaluator 상세
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 2세대 컨텍스트 엔지니어링 상세
- [agent-build-harness](/insights/agent-build-harness.md) — 실제 구현 패턴 (Constitution + eval.sh + RALPH Loop)
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md) — 하네스 규모 결정 기준
