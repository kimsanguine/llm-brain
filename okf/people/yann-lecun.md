---
type: person
title: Yann LeCun
description: Meta Chief AI Scientist 겸 NYU 교수.
tags:
- yann-lecun
- meta
- deep-learning
- turing-award-2018
- world-model
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://yann.lecun.com
- https://ai.meta.com
- https://twitter.com/ylecun
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Yann LeCun

Meta Chief AI Scientist 겸 NYU 교수. 딥러닝 1세대 개척자로 CNN의 원조인 **LeNet**을 고안했으며, 2018년 Turing Award를 Geoffrey Hinton·Yoshua Bengio와 공동 수상했다.

## 배경 및 초기 경력

프랑스 출신으로 파리 6대학(피에르-마리 퀴리)에서 박사학위를 취득했다. AT&T Bell Labs 재직 중인 1989년 역전파(backpropagation)를 CNN에 적용한 **LeNet**을 발표했다. LeNet은 필기 숫자 인식(MNIST)에 실용화되어 실제 수표 판독 시스템에 배포됐다.

이 연구는 2012년 [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md)의 직접적 선조로 평가받는다. AlexNet은 LeNet의 아키텍처 원리를 대규모 GPU 학습으로 확장한 것이다.

## Turing Award 2018

Geoffrey Hinton([geoffrey-hinton](/people/geoffrey-hinton.md))·Yoshua Bengio와 함께 "딥러닝을 통한 개념적·공학적 돌파구"로 ACM Turing Award를 수상했다. 세 사람은 각자 다른 방향에서 딥러닝 리바이벌을 이끌었다: Hinton(확률 모델·표현 학습), Bengio(순환 신경망·언어 모델), LeCun(합성곱 신경망·컴퓨터 비전).

## Meta FAIR 책임자

Facebook AI Research(FAIR)를 2013년 창설해 이끌고 있다. FAIR는 학술 오픈 퍼블리싱 문화를 유지하며 PyTorch, Detectron2, faiss 등 주요 오픈소스 인프라를 배출했다.

**Llama 패밀리(Llama 1–3, Llama 4)**의 배경 조직이기도 하다. LeCun은 Meta의 open-source LLM 전략을 공개적으로 지지하며 "AI는 오픈 인프라가 되어야 한다"는 입장을 반복해서 표명했다.

## Autoregressive LLM 비판 및 JEPA

LeCun은 현행 autoregressive LLM이 인간 수준 지능에 도달하기에 구조적으로 부족하다고 주장한다. 핵심 비판:

- 토큰 단위 예측은 세계의 인과 구조를 학습하지 못한다.
- 고차원 latent space에서 사전적으로 미래를 예측(planning)하는 능력이 결여되어 있다.

대안으로 제안하는 아키텍처가 **Joint Embedding Predictive Architecture(JEPA)**다. JEPA는 이미지·비디오 등 지각 입력을 latent space에서 예측해 world model을 형성하는 방식으로, LLM의 텍스트 중심성을 벗어난다.

이 논쟁은 [omnimodality](/concepts/omnimodality.md) 방향 및 world model 연구 트렌드와 직결된다.

## 딥러닝 1세대 내 위치

LeCun, Hinton, Bengio 세 사람은 AI Winter 기간 동안 신경망 연구를 고수한 공통점이 있으나, 현재 AGI 접근법에 대한 견해는 갈린다:

- [geoffrey-hinton](/people/geoffrey-hinton.md) — Transformer 기반 현 경로의 위험성을 경고하며 AI 안전 우려 강조.
- Bengio — AI 정책·거버넌스에 집중.
- LeCun — 현 LLM 경로 자체를 기술적으로 부정하며 JEPA/world model로 전환 주장.

## 관련 페이지

- [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [geoffrey-hinton](/people/geoffrey-hinton.md)
- [karpathy](/people/karpathy.md)
- [ilya-sutskever](/people/ilya-sutskever.md)
- ai-paper-learning-path
- [omnimodality](/concepts/omnimodality.md)
- [frontier-labs-comparison](/concepts/frontier-labs-comparison.md)
