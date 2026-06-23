---
type: paper
title: Attention Is All You Need (2017)
description: Google Brain · Google Research가 NeurIPS 2017에 발표.
tags:
- transformer
- attention
- foundational-paper
- google-brain
- sequence-modeling
timestamp: '2026-06-04'
x-llmbrain-domain:
- AI/LLM
- research
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/1706.03762
- https://research.google/pubs/attention-is-all-you-need/
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Attention Is All You Need (2017)

## 핵심 요약

Google Brain · Google Research가 NeurIPS 2017에 발표. **Transformer 아키텍처** 첫 제시. RNN/LSTM 없이 attention만으로 sequence-to-sequence 학습. 이후 모든 LLM(GPT, BERT, T5, Claude, Gemini)의 기반.

저자: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin.

## 핵심 기여

### 1. Self-Attention 메커니즘
- Query·Key·Value 행렬 곱셈으로 sequence 내 token 간 관계 직접 계산
- O(n²) 복잡도지만 병렬화 가능 (RNN의 sequential 의존성 제거)

### 2. Multi-Head Attention
- 여러 attention head로 다양한 관계 학습 (문법·의미·위치 등)
- 8 heads (논문 기준)

### 3. Positional Encoding
- attention 자체는 순서 무관이라 위치 정보 별도 주입
- sinusoidal positional encoding 제시

### 4. Encoder-Decoder 구조
- Encoder: 입력 sequence → context vectors
- Decoder: context + autoregressive 생성

## 성능 (논문 보고)

WMT 2014 영어→독일어 번역: **BLEU 28.4** (당시 SOTA), 영어→프랑스어 BLEU 41.8. 학습 시간 3.5일 (8 P100 GPU) — RNN 기반 기존 모델 대비 훨씬 짧음.

## 본 wiki에서의 위치

- 본 wiki의 모든 LLM 도구 (Claude, GPT, Gemini)의 아키텍처 출처
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) (강의에서 다룬 CNN·ResNet 진화의 다음 단계)
- ai-paper-learning-path의 가장 우선 추천 논문
- 후속 발전: BERT (2018), GPT-2/3 (2019-2020), Chinchilla, LLaMA, Claude 시리즈
- [claude-code](/tools/claude-code.md)·[claude-code-agent-system](/tools/claude-code-agent-system.md) — Transformer 기반 코딩 AI 도구의 실제 구현
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) — edge 환경 Transformer 추론 응용 스택
- [ai-pm-role](/concepts/ai-pm-role.md) — PM 관점에서 Transformer 전환이 가져온 제품 패러다임 변화
- 관련 논문: [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md) (Transformer → 대형 LLM 확장), [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) (딥러닝 역사에서의 선행 milestone)

## 후속 영향

- **Scaling laws** ([dario-amodei](/people/dario-amodei.md) OpenAI 시절 정착) — Transformer가 scale에 잘 반응
- **Decoder-only LLM** ([karpathy](/people/karpathy.md) nanoGPT 같은 reference) — GPT family
- **Encoder-only** — BERT, T5
- **Multimodal Transformer** — Vision Transformer, [omnimodality](/concepts/omnimodality.md), [interaction-models](/concepts/interaction-models.md)

## 2026-06-03 보강: attention 효율화 계보

AI Human 논문 큐레이션은 이 논문 이후 attention 연구를 세 단계로 정리했다. 첫째, **Relative Position Representations (2018)**는 token 간 상대 거리를 attention score에 넣어 절대 위치 encoding의 한계를 보완했다. 둘째, **FlashAttention (2022)**은 exact attention을 유지하면서 GPU 메모리 IO를 줄이는 tiling/online-softmax/recomputation 설계로 긴 sequence 학습을 실용화했다. 셋째, **Native Sparse Attention (2025)**은 compressed/selected/sliding 3개 attention 분기를 학습 가능한 sparse 구조로 묶어 100K+ token 맥락의 비용을 낮추려는 흐름이다.

제품 관점에서 중요한 점은 attention이 더 이상 추상 알고리즘만이 아니라 배포 비용의 직접 변수라는 것이다. 긴 문서 분석, 코드베이스 이해, 장기 메모리 에이전트는 [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)에서 latency·memory·cost 검증을 함께 해야 한다.

## 관련 개념
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- ai-paper-learning-path
- [karpathy](/people/karpathy.md)
- [dario-amodei](/people/dario-amodei.md)
- [omnimodality](/concepts/omnimodality.md)
- [claude-code](/tools/claude-code.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md)
- [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md)
