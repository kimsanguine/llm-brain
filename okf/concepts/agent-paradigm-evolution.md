---
type: concept
title: Agent Paradigm Evolution
description: '단일 prompt에 instruction + context를 모두 넣고 LM이 답하게 함. 한계: 도구·외부 상태 접근 불가,
  hallucination 다수.'
tags:
- agent
- agent-framework
- evolution
- synthesis-hub
- multi-agent
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- agent
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://www.anthropic.com/research/swe-bench-sonnet
- https://arxiv.org/abs/2405.15793
- https://blog.anthropic.com/research/agent-architecture
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Agent Paradigm Evolution

## 핵심 요약

LM 에이전트 설계는 2023-2026 동안 **4단계 진화**를 거쳤다: ① Prompt-only → ② Harness (외부 시스템) → ③ ACI (Agent-Computer Interface) → ④ Multi-agent orchestration. 본 페이지는 본 wiki의 5+ 메가 허브를 묶어 진화 흐름을 한눈에 본다.

## 4단계 진화

### Stage 1 — Prompt-only (2022-2023)

단일 prompt에 instruction + context를 모두 넣고 LM이 답하게 함. 한계: 도구·외부 상태 접근 불가, hallucination 다수.

### Stage 2 — Harness 등장 (2023-2024)

[harness-engineering-evolution](/concepts/harness-engineering-evolution.md) 참고. Mitchell Hashimoto 원칙: "실수가 구조적으로 재발 불가하게 시스템 변경". 에이전트 외부에 평가·재시도·메모리 시스템을 두기 시작.

[agent-harness-pattern](/concepts/agent-harness-pattern.md) = OpenAI 4 Pillars (Tools/Reasoning/Memory/Steering) + Anthropic 5 Principles 통합. **Generator-Evaluator 분리가 핵심** — [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) (PGE 3-에이전트 패턴).

본 wiki 적용 사례: [agent-build-harness](/insights/agent-build-harness.md) (/build v3, Constitution 3파일, hplan cycle).

### Stage 3 — ACI 패러다임 (2024-)

Princeton의 SWE-agent 논문이 제시: [swe-agent-aci](/tools/swe-agent-aci.md). **LM 에이전트는 "새 카테고리의 end user"** — 인간이 IDE를 쓰듯 specially-built interface 필요. SWE-bench 12.5% / HumanEvalFix 87.7% SOTA로 입증.

ACI 본질:
- 파일 생성·편집, 리포지토리 탐색, 테스트 실행을 LM 친화적으로 추상화
- 인간용 GUI/CLI ≠ LM ACI

본 wiki 적용: [claude-code-agent-system](/tools/claude-code-agent-system.md)의 Bash/Read/Edit/Glob tool이 사실상 ACI. `wiki_app/`의 `/api/llm/...` endpoint도 LM-readable ACI 후보.

### Stage 4 — Multi-agent orchestration (2024-)

[single-vs-multi-agent](/concepts/single-vs-multi-agent.md) 결정 프레임워크: 병렬화 가능성·컨텍스트 포화·읽기/쓰기 구조 3축. 멀티: +81% (병렬 가능) / -70% (순차 dependent).

[context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 에이전트 성패는 모델이 아닌 컨텍스트 설계. 3패턴: 압축·역할 분리·지속 메모리.

본 wiki 적용: `superpowers:dispatching-parallel-agents` skill + `isolation: worktree` 패턴. 본 페이지를 만든 parallel agent dispatch가 직접 사례.

## 진화 축 vs 본 wiki 메가 허브

| 진화 단계 | 본 wiki 메가 허브 (degree top) |
|---|---|
| Stage 2 (harness) | [agent-harness-pattern](/concepts/agent-harness-pattern.md) (25) · [agent-build-harness](/insights/agent-build-harness.md) (24) |
| Stage 3 (ACI) | [swe-agent-aci](/tools/swe-agent-aci.md) (6) · [claude-code-agent-system](/tools/claude-code-agent-system.md) (18) |
| Stage 4 (multi-agent) | [single-vs-multi-agent](/concepts/single-vs-multi-agent.md) (10) · [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) (12) |
| 평가 게이트 | [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) (6) · [ai-governance-verification](/concepts/ai-governance-verification.md) (6) |

## 차세대 진화 예측 (2026-)

본 wiki의 신규 ingest (`gemini-spark`, `openai-agents-sdk`, `swe-agent-aci`, `interaction-models`)에서 보이는 흐름:

1. **Long-running background agent** — [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) (사용자 1명이 동시 굴리는 에이전트 수 N이 KPI)
2. **Vertical agent + 도메인 깊이** — [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md) (워크플로·작업 표면·권한 게이트 통합)
3. **Pricing 진화** — [agent-pricing-model](/concepts/agent-pricing-model.md) (Seat → Usage → Outcome → Domain Package SKU)
4. **음성 패러다임 통합** — [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) + [interaction-models](/concepts/interaction-models.md) (200ms full-duplex) + [voice-ai-stack](/concepts/voice-ai-stack.md) (음성 인터페이스 레이어 전반)
5. **경량 적응 (fine-tuning 없이)** — [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md) LoRA 방식이 에이전트 특화 모델 경량화의 표준 후보
6. **인프라 정규화** — [llm-deployment-patterns](/concepts/llm-deployment-patterns.md) (서빙 레이어 설계·비용 최적화)

[demis-hassabis](/people/demis-hassabis.md)가 이끈 DeepMind의 AlphaFold→Gemini 궤적은 Stage 3→4 진화의 실증 사례다 — 전문 도메인 AI에서 범용 멀티모달 에이전트로의 전환이 에이전트 패러다임 진화와 궤를 같이 한다.

## 본 wiki에서의 위치

- 5개 메가 허브를 묶는 synthesis hub
- 신규 [swe-agent-aci](/tools/swe-agent-aci.md)의 ACI 개념을 기존 harness 클러스터와 통합
- [ai-pm-role](/concepts/ai-pm-role.md) 등 PM 역할 페이지와 "에이전트 시대 PM이 무엇을 결정하나" 맥락 가교

## 관련 개념

- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [agent-build-harness](/insights/agent-build-harness.md)
- [swe-agent-aci](/tools/swe-agent-aci.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md)
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md)
- [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)
- [agent-pricing-model](/concepts/agent-pricing-model.md)
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md)
- [interaction-models](/concepts/interaction-models.md)
- [ai-governance-verification](/concepts/ai-governance-verification.md)
- [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)
- [voice-ai-stack](/concepts/voice-ai-stack.md)
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md)
- [demis-hassabis](/people/demis-hassabis.md)
