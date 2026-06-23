---
type: concept
title: Classical ML and Tabular Foundation Models
description: 정형 데이터 ML의 뿌리는 두 축으로 잡는 것이 좋다.
tags:
- ml-classics
- tabular-ml
- svm
- decision-tree
- foundation-model
timestamp: '2026-06-24'
x-llmbrain-domain:
- AI education
- machine learning
- tabular data
x-llmbrain-created: '2026-06-24'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Classical ML and Tabular Foundation Models

## 핵심 요약

정형 데이터 ML의 뿌리는 두 축으로 잡는 것이 좋다. 결정트리는 데이터를 분기하며 불순도를 줄이고, SVM은 결정 경계의 마진을 최대화해 일반화를 노린다.

2025년 이후 TabPFN/TabICL 계열은 이 고전 베이스라인을 사전학습 + in-context learning + 증류로 재해석한다. 그래서 정형 데이터 강의는 "고전 ML vs 딥러닝"보다 "고전 베이스라인이 파운데이션 모델로 어떻게 재편되는가"로 설명하는 편이 낫다.

## 작동 원리

### 마진 기반: SVM

Cortes & Vapnik의 Support-Vector Networks는 최대 마진 초평면을 분류의 핵심 원리로 세운다. 커널 트릭은 데이터를 고차원 특징 공간으로 보낸 효과를 내면서도 명시적 고차원 계산을 피한다. 소프트 마진은 선형 분리가 안 되는 현실 데이터에서 오차 허용과 일반화의 균형을 잡는 장치다.

강의에서는 SVM을 "고차원 데이터에서 경계 자체보다 경계 주변 여유 공간을 최적화하는 모델"로 설명하면 직관이 빠르다. [ml-classification-algorithms](/lecture/ml-classification-algorithms.md)의 SVM 실습과 바로 연결된다.

### 분기 기반: 결정트리

Quinlan의 ID3는 엔트로피와 정보 이득으로 속성을 고르고, 데이터를 재귀적으로 분할해 사람이 읽을 수 있는 규칙을 만든다. 이후 C4.5, CART, Random Forest, GBDT, XGBoost, LightGBM, CatBoost로 이어지는 트리 기반 학습의 사상적 출발점이다.

트리 계열의 장점은 단순 정확도만이 아니라 설명 가능성이다. 신용평가, 이탈 예측, 의료 진단처럼 왜 그런 판단을 했는지 설명해야 하는 정형 데이터 문제에서 여전히 강한 베이스라인이다.

### 정형 데이터 파운데이션 모델

TabPFN-2.5는 사전학습된 트랜스포머가 추가 학습 없이 in-context learning으로 분류·회귀를 수행하는 방향을 보여준다. raw 기준으로 최대 5만 행·2천 특징까지 지원하고, TabArena에서 튜닝된 트리 모델과 4시간 AutoML 앙상블 수준의 정확도를 겨냥한다.

핵심 변화는 "정형 데이터는 트리 모델이 딥러닝을 이긴다"는 통념이 약해지고 있다는 점이다. 다만 production에서는 지연시간과 비용이 중요하므로, TabPFN류 모델을 경량 MLP나 트리 앙상블로 증류하는 배포 패턴까지 함께 봐야 한다.

## 활용 사례

- 소규모 고차원 분류: 임베딩 분류, 이상탐지, 의료·바이오 데이터에서 SVM은 여전히 견고한 baseline이다.
- 해석 가능한 정형 데이터 모델: 결정트리/GBDT 계열은 feature split, gain, rule path로 설명 가능성을 제공한다.
- 빠른 PoC: TabPFN/TabICL 계열은 고객별 schema가 다른 B2B SaaS에서 "학습 없는 즉시 예측" 후보가 된다.
- 저지연 production: 파운데이션 모델의 예측 능력을 증류해 경량 모델로 배포하는 방식이 현실적이다.

## habix/강의와의 연결점

AI Human Module 3에서는 고전 ML을 "시험용 알고리즘 목록"으로 끝내면 안 된다. SVM의 마진, 결정트리의 정보 이득, Bagging/AdaBoost의 앙상블 사고를 잡아야 TabPFN/TabICL 같은 tabular foundation model의 의미가 보인다.

PM 관점에서는 이 계보가 [agent-harness-pattern](/concepts/agent-harness-pattern.md)의 도구 레이어와 연결된다. 에이전트가 고객 데이터를 받았을 때 매번 커스텀 학습을 돌리는 대신, tabular foundation model 또는 증류된 lightweight model을 빠른 진단 도구로 붙일 수 있다.

## 관련 개념

- ai-paper-learning-path
- [ml-classification-algorithms](/lecture/ml-classification-algorithms.md)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
