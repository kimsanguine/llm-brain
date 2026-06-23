---
type: paper
title: Language Models are Few-Shot Learners (GPT-3, 2020)
description: OpenAI가 NeurIPS 2020에 발표.
tags:
- gpt-3
- foundational-paper
- few-shot
- in-context-learning
- scaling-laws
- openai
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- research
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/2005.14165
- https://openai.com/research/language-models-are-few-shot-learners
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Language Models are Few-Shot Learners (GPT-3, 2020)

## 핵심 요약

OpenAI가 NeurIPS 2020에 발표. **175B 파라미터 GPT-3** 첫 제시. 핵심 발견: **scale up만으로 few-shot · zero-shot in-context learning이 emergent**. fine-tuning 없이 prompt에 예시 몇 개만 줘도 task 수행. 현재 ChatGPT·GPT-4 family의 직접 조상.

저자: Tom B. Brown 외 30+명 (OpenAI). 1저자 Brown.

## 핵심 기여

### 1. Scaling 검증
- 125M → 13B → 175B 단계적 학습 — 모든 task에서 scale에 따라 성능 monotonic 향상
- [dario-amodei](/people/dario-amodei.md) 등이 정착시킨 "scaling laws"의 결정적 검증

### 2. In-Context Learning 등장
- prompt에 task 예시 (k=0/1/few-shot)만 줘도 fine-tuning 없이 학습
- **새로운 패러다임**: 모델 한 번 학습 후 prompt로 모든 task 처리

### 3. 메타 발견: emergent capabilities
- 작은 모델에선 안 보이던 능력이 큰 모델에서 갑자기 등장
- 산술·번역·QA·코드생성 모두 175B에서 의미 있는 수준

### 4. 학습 데이터
- Common Crawl (filtered), WebText2, Books1+2, Wikipedia
- 약 500B tokens

## 한계 (논문에서 자체 명시)

- 사실 정확성 부족
- 학습 데이터 시점 이후 정보 없음
- 사회적 편향 학습
- "Helpful, Harmless, Honest" 부재 — 후속 anthropic Constitutional AI ([dario-amodei](/people/dario-amodei.md))가 해결 시도

## 본 wiki에서의 위치

- openai 핵심 milestone
- ChatGPT (2022.11) 의 모델적 기반 — GPT-3.5 (InstructGPT) → GPT-4 family 진화
- ai-paper-learning-path의 LLM 시작점
- [sam-altman](/people/sam-altman.md)·[ilya-sutskever](/people/ilya-sutskever.md)·[dario-amodei](/people/dario-amodei.md)·[karpathy](/people/karpathy.md) 시대 OpenAI 작품
- [claude-code](/tools/claude-code.md) — GPT-3 계보 LLM 기반 도구 중 Anthropic 측 실제 제품 비교점
- [openai-realtime-api](/tools/openai-realtime-api.md)·[openai-agents-sdk](/tools/openai-agents-sdk.md) — GPT-3 이후 OpenAI 도구 진화의 직접 후손
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) — 강의에서 다루는 scaling law · few-shot 개념의 원전
- [constitutional-ai-anthropic-2022](/papers/constitutional-ai-anthropic-2022.md) — GPT-3의 safety 한계를 Anthropic이 CAI로 응답한 논문
- 관련 논문: [attention-is-all-you-need](/papers/attention-is-all-you-need.md) (Transformer 기반 아키텍처 원전)

## 후속 발전

- InstructGPT (2022) — RLHF 도입
- ChatGPT (2022.11) — 대중화
- GPT-4, GPT-4o, o1, GPT-5 — 추론 + 멀티모달 + tool use
- 경쟁: Claude family (anthropic), Gemini, LLaMA

## 관련 개념
- openai
- ai-paper-learning-path
- [sam-altman](/people/sam-altman.md)
- [ilya-sutskever](/people/ilya-sutskever.md)
- [dario-amodei](/people/dario-amodei.md)
- [karpathy](/people/karpathy.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [claude-code](/tools/claude-code.md)
- [openai-realtime-api](/tools/openai-realtime-api.md)
- [openai-agents-sdk](/tools/openai-agents-sdk.md)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [constitutional-ai-anthropic-2022](/papers/constitutional-ai-anthropic-2022.md)
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md)
