---
type: paper
title: ImageNet Classification with Deep Convolutional Neural Networks (AlexNet, 2012)
description: University of Toronto 팀(Krizhevsky · ilya-sutskever · Geoffrey Hinton)이
  NIPS 2012에 발표.
tags:
- alexnet
- imagenet
- cnn
- deep-learning
- foundational-paper
- computer-vision
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- research
- vision
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html
- https://en.wikipedia.org/wiki/AlexNet
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# ImageNet Classification with Deep CNN (AlexNet, 2012)

## 핵심 요약

University of Toronto 팀(Krizhevsky · [ilya-sutskever](/people/ilya-sutskever.md) · Geoffrey Hinton)이 NIPS 2012에 발표. **CNN + GPU 학습 + 대규모 데이터셋(ImageNet)** 조합으로 ILSVRC 2012 우승 — top-5 error 15.3% (2위 26.2%). **딥러닝 revival 결정적 계기**.

## 핵심 기여

### 1. 깊은 CNN의 실용성 입증
- 8 layers (5 conv + 3 FC), 60M parameters
- 당시 SOTA보다 11% 큰 폭 성능 차이

### 2. GPU 가속 학습 정착
- NVIDIA GTX 580 2장 (3GB each)으로 일주일 학습
- 이전: CPU로 수개월 → GPU로 며칠 → 학습 가능성 자체가 변화

### 3. 핵심 테크닉
- **ReLU** activation (tanh 대비 학습 속도 ↑)
- **Dropout** (overfitting 완화)
- **Data augmentation** (crop·flip·PCA color jitter)
- **Local Response Normalization** (이후 BatchNorm으로 대체)

### 4. ImageNet 같은 대규모 데이터셋의 가치 입증
- 1.2M 학습 이미지 × 1000 classes
- 이전: 작은 데이터셋 (~10K)으로는 깊은 net 학습 불가
- "데이터·모델·연산" 삼각 동시 scaling 패러다임 시작

## 본 wiki에서의 위치

- **딥러닝 revival의 시작점** — 이 paper 이후 컴퓨터 비전 → NLP → 멀티모달 전 영역에서 딥러닝 표준화
- [ilya-sutskever](/people/ilya-sutskever.md) 공동 저자 — 후 OpenAI Chief Scientist
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) 강의의 CNN 챕터 직접 출처; [ml-classification-algorithms](/lecture/ml-classification-algorithms.md) (분류 알고리즘 진화에서 CNN의 위치)
- ai-paper-learning-path의 vision/CNN 영역 시작점
- 진화 라인: AlexNet → VGG → ResNet → Inception → DenseNet → Vision Transformer
- [andrew-ng](/people/andrew-ng.md) — Coursera Deep Learning Specialization CNN 강의의 역사적 레퍼런스
- [hyperclova-x-omni](/tools/hyperclova-x-omni.md) — vision encoder 계보에서 AlexNet이 기원이 된 multimodal 모델 사례
- 관련 논문: [attention-is-all-you-need](/papers/attention-is-all-you-need.md) (AlexNet 이후 vision에도 적용된 Transformer 패러다임)

## 후속 영향

- ResNet (2015, He et al.) — skip connection으로 100+ layers 가능
- Vision Transformer (2020) — [attention-is-all-you-need](/papers/attention-is-all-you-need.md) 패러다임을 vision에 적용
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) 같은 production CV stack도 AlexNet의 직접 후손
- 멀티모달 ([omnimodality](/concepts/omnimodality.md), [gemini-omni-flash](/tools/gemini-omni-flash.md)) — vision encoder의 기원

## 인물 영향력

- Hinton: AI "godfather", 2024 Nobel Physics
- [ilya-sutskever](/people/ilya-sutskever.md): 후 OpenAI → Safe Superintelligence Inc
- Krizhevsky: 후 Google Brain (조용히 사임)

## 관련 개념
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [ml-classification-algorithms](/lecture/ml-classification-algorithms.md)
- ai-paper-learning-path
- [ilya-sutskever](/people/ilya-sutskever.md)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)
- [omnimodality](/concepts/omnimodality.md)
- [andrew-ng](/people/andrew-ng.md)
- [hyperclova-x-omni](/tools/hyperclova-x-omni.md)
- [gemini-omni-flash](/tools/gemini-omni-flash.md)
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md)
