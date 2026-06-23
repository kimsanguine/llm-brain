---
type: concept
title: LLM 양자화와 압축
description: LLM 양자화는 모델 품질을 크게 잃지 않으면서 메모리와 추론 비용을 줄이는 serving 기술이다.
tags:
- quantization
- llm-serving
- compression
- cost-optimization
timestamp: '2026-06-23'
x-llmbrain-domain:
- AI/LLM
x-llmbrain-created: '2026-06-23'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM 양자화와 압축

## 핵심 요약

LLM 양자화는 모델 품질을 크게 잃지 않으면서 메모리와 추론 비용을 줄이는 serving 기술이다. LLM.int8()은 이상치 차원을 분리해 8비트 행렬곱을 실용화했고, AWQ는 activation-aware weight scaling으로 4비트 배포 품질을 높였으며, QuaRot은 회전 변환으로 outlier를 줄여 4비트 추론을 안정화한다.

## 작동 원리

### 1. 이상치가 양자화 품질을 좌우한다

LLM.int8()은 대형 Transformer에서 일부 outlier 차원이 8비트 양자화 오류를 크게 만든다는 점을 포착했다. 대부분의 행렬곱은 int8로 처리하고, 이상치 차원은 별도 고정밀 경로로 처리해 추가 학습 없이도 큰 모델을 낮은 메모리로 로딩한다.

### 2. 중요한 weight만 보호한다

AWQ는 모든 weight를 똑같이 보호하지 않는다. activation 분포를 보고 출력 품질에 큰 영향을 주는 weight channel을 식별한 뒤 scaling을 적용한다. 이는 production 관점에서 "전부 고정밀로 두기"보다 **품질에 민감한 부분만 보호**하는 비용 최적화다.

### 3. 회전으로 outlier를 평탄화한다

QuaRot은 Hadamard rotation 같은 회전 변환으로 activation과 weight의 outlier를 더 균일하게 만든 뒤 4비트 양자화를 적용한다. 핵심은 양자화 전에 분포를 바꿔, 낮은 비트에서도 거리와 내적 계산이 덜 깨지게 하는 것이다.

## 활용 사례

- 로컬 LLM 실행: 제한된 VRAM에서 7B~70B 모델을 올릴 때 기본 선택지다.
- 배치 추론: 동일 품질을 더 낮은 GPU 메모리와 전력으로 처리한다.
- edge/온디바이스 AI: 모델 크기와 지연시간이 제품 UX를 직접 결정하는 환경에서 필요하다.
- 모델 라우팅: 비싼 frontier API 호출 전, 양자화된 local/open 모델로 처리 가능한 작업을 분리한다.

## habix/강의와의 연결점

Ch06 LLM 효율화는 LoRA/QLoRA만으로 끝내면 부족하다. 수강생에게는 "학습 비용을 줄이는 PEFT"와 "추론 비용을 줄이는 양자화"를 나눠 설명해야 한다. 제품 관점의 질문은 "이 모델을 어디서 학습할까?"뿐 아니라 "이 모델을 매일 얼마에 서빙할까?"다.

## 관련 개념

- [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md)
- ai-paper-learning-path
- [agent-pricing-model](/concepts/agent-pricing-model.md)
