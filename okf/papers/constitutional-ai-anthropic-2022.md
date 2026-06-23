---
type: paper
title: 'Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)'
description: anthropic이 2022.12 arXiv에 발표.
tags:
- constitutional-ai
- alignment-paper
- rlaif
- anthropic
- alignment
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- research
- alignment
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/2212.08073
- https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Constitutional AI: Harmlessness from AI Feedback (2022)

## 핵심 요약

anthropic이 2022.12 arXiv에 발표. **Constitutional AI (CAI)** 방법론 첫 정식 제시. RLHF의 한계(인간 라벨러 부담·일관성 문제)를 해결 — **AI가 사전 정의된 "헌법(Constitution)" 원칙으로 다른 AI 응답을 평가·교정**. 본 wiki anthropic safety-first 포지셔닝의 직접 출처.

저자: Yuntao Bai 외 다수 (Anthropic). [dario-amodei](/people/dario-amodei.md) 주도.

## 핵심 기여

### 1. RLAIF (RL from AI Feedback)
- RLHF (human feedback) → RLAIF (AI feedback)으로 확장
- 인간 라벨링 부담 ↓, 일관성 ↑, 확장성 ↑

### 2. 2단계 학습
- **SL 단계 (Supervised Learning)**:
  - 모델이 자기 응답을 평가
  - "이 응답이 헌법 N번 원칙에 어긋나나?" → 자가 수정
- **RL 단계**:
  - 헌법 기준으로 응답 쌍 (A vs B) 비교
  - 더 헌법에 부합하는 응답을 reward로 학습

### 3. "헌법(Constitution)"의 구성
- 자연어로 명시된 원칙 (예: "차별적 발언 금지", "사실 정확성 우선")
- UN 인권선언 등 외부 표준 인용 가능
- 운영자가 모델 별로 헌법 customize

### 4. Helpful + Harmless 양립
- 기존 RLHF: helpful ↔ harmless 트레이드오프
- CAI: 두 축 동시 향상 가능 입증

## 본 wiki에서의 위치

- anthropic 회사의 핵심 방법론 출처
- [ai-governance-verification](/concepts/ai-governance-verification.md) (인지적 항복 + agent 보안 설계) 의 paper 출처
- [dario-amodei](/people/dario-amodei.md)·Daniela Amodei 주도 연구의 대표작
- [frontier-labs-comparison](/concepts/frontier-labs-comparison.md) 에서 Anthropic = "safety-first"의 정량 근거
- [claude-code](/tools/claude-code.md)·[claude-code-agent-system](/tools/claude-code-agent-system.md) — CAI가 실제 적용된 Anthropic 도구 (Claude 모델 기반)
- [ai-pm-role](/concepts/ai-pm-role.md) — PM 관점에서 alignment 책임과 CAI 원칙의 제품 반영
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md) — GPT-3의 safety 한계가 CAI 개발의 직접 동기; 두 논문 비교로 alignment 진화 추적 가능

## 후속 발전

- Claude 1.0 (2023) — CAI 적용 첫 제품
- Claude 2/3/4 — CAI 점진 진화
- **Responsible Scaling Policy (RSP)** — capability tier별 단계 출시 (CAI는 그 안의 safety 방법론)
- 영향: 다른 lab들도 RLAIF 변형 도입 (openai 등)

## 한계 / 비판

- "헌법" 자체가 누구 가치관인가? — universal 어렵움
- AI가 AI 평가의 정확성 — 한계는 underlying model
- RLHF 완전 대체는 아님 — hybrid (HF + AI feedback) 패턴이 실제 production

## 관련 개념
- anthropic
- [ai-governance-verification](/concepts/ai-governance-verification.md)
- [dario-amodei](/people/dario-amodei.md)
- [frontier-labs-comparison](/concepts/frontier-labs-comparison.md)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) (Generator·Evaluator 분리 정신 = CAI 정신)
- ai-paper-learning-path
- [claude-code](/tools/claude-code.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md)
