---
type: paper
title: 'InstructGPT: Training language models to follow instructions with human feedback
  (2022)'
description: OpenAI가 2022년 발표 (arxiv 2203.02155).
tags:
- instructgpt
- rlhf
- alignment-paper
- alignment
- openai
- chatgpt-foundation
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- research
- alignment
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/2203.02155
- https://openai.com/research/instruction-following
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# InstructGPT: Training language models to follow instructions with human feedback (2022)

## 핵심 요약

OpenAI가 2022년 발표 (arxiv 2203.02155). 저자: Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, John Schulman, Jacob Hilton, Fraser Kelton, Luke Miller, Maddie Simens, Amanda Askell, Peter Welinder, Paul Christiano, Jan Leike, Ryan Lowe.

**RLHF(Reinforcement Learning from Human Feedback)** 기법을 정립한 논문. GPT-3 → ChatGPT(2022.11) 전환의 핵심 기술 출처. "도움이 되고, 무해하며, 정직한(helpful, harmless, honest)" AI 정렬의 실증적 첫 성공 사례.

## 3단계 훈련 파이프라인

### 1단계: SFT (Supervised Fine-Tuning)
- 사람이 작성한 이상적 응답 데이터(~13,000개 프롬프트) 수집
- GPT-3를 해당 데이터로 지도 학습
- 결과: 지시 따르기 능력 획득, 단 alignment 미완성

### 2단계: Reward Model (RM) 학습
- 같은 프롬프트에 대한 여러 응답을 사람이 순위 매김
- 6B 파라미터 별도 모델 학습 → 응답 품질 점수 출력
- 핵심: "어떤 답이 더 좋은가" 판단 기준을 모델로 내재화

### 3단계: PPO RL Fine-Tuning
- SFT 모델을 RM 점수를 보상으로 PPO(Proximal Policy Optimization)로 최적화
- KL divergence 페널티로 원본 GPT-3 분포에서 너무 멀어지는 것 방지
- 결과: 사람 평가자가 GPT-3보다 InstructGPT를 압도적으로 선호

## 핵심 발견

- **175B GPT-3 < 1.3B InstructGPT**: 파라미터 100배 작은 모델이 사람 선호도에서 우위
- 정렬 비용 ≠ 성능 저하: RLHF 후에도 NLP 벤치마크 성능 유지
- 환각(hallucination), 독성(toxicity) 감소 — 단 완전 해결 아님
- "aligned but not fully safe": alignment ≠ safety의 분리 명시

## alignment 패러다임의 분기점

이 논문을 기점으로 LLM 개발 경쟁의 목표가 "더 큰 모델"에서 "더 잘 정렬된 모델"로 전환. 두 갈래 정렬 접근법이 분화:

| 접근법 | 대표 | 특징 |
|--------|------|------|
| RLHF | OpenAI (InstructGPT → ChatGPT → GPT-4) | 인간 피드백 직접 활용, 고비용 |
| CAI/RLAIF | Anthropic (Claude 시리즈) | AI 피드백으로 인간 의존도 감소 |

## 본 wiki에서의 위치

- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md) — 직접 후속 논문. GPT-3를 기반 모델로 사용
- [constitutional-ai-anthropic-2022](/papers/constitutional-ai-anthropic-2022.md) — RLHF의 대안/발전 계보. Anthropic이 RLHF 한계 극복용으로 CAI 제시
- openai — InstructGPT → ChatGPT → GPT-4 제품 라인의 기술 핵심
- [sam-altman](/people/sam-altman.md) — ChatGPT 출시(2022.11) 결정의 주체, RLHF 상용화 가속
- [ilya-sutskever](/people/ilya-sutskever.md) — OpenAI Chief Scientist, RLHF 연구 방향 주도
- [dario-amodei](/people/dario-amodei.md) — 당시 OpenAI VP of Research; 이후 Anthropic 창업 후 CAI로 대안 제시
- 관련 논문: [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md) (SFT 단계를 PEFT로 경량화하는 결합 패턴), [attention-is-all-you-need](/papers/attention-is-all-you-need.md) (Transformer 기반 모델 전체의 공통 출처)

## 역사적 맥락

```
2020.06 GPT-3 발표 (few-shot learning)
2022.03 InstructGPT 논문 공개 (RLHF 정립)
2022.11 ChatGPT 출시 → 100만 사용자 5일 달성
2023.03 GPT-4 발표
2022.12 Anthropic, Constitutional AI 논문 (CAI/RLAIF)
```

## 후속 영향

- **ChatGPT** — InstructGPT 기반의 직접 상용 제품, AI 대중화 원점
- **오픈소스 RLHF** — Alpaca, Vicuna, OpenAssistant 등 RLHF 재현 프로젝트 폭증
- **Reward hacking 문제** 가시화 → 이후 Constitutional AI, RLAIF, DPO(Direct Preference Optimization) 연구 동기
- **규제 논의 촉발** — EU AI Act, 미국 AI EO의 직접적 계기

## 관련 개념
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md)
- [constitutional-ai-anthropic-2022](/papers/constitutional-ai-anthropic-2022.md)
- openai
- [sam-altman](/people/sam-altman.md)
- [ilya-sutskever](/people/ilya-sutskever.md)
- [dario-amodei](/people/dario-amodei.md)
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md)
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md)
