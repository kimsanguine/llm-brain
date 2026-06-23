---
type: concept
title: 긴 컨텍스트와 메모리 관리
description: 긴 컨텍스트 문제는 "입력을 더 많이 넣기"가 아니라 무엇을 보존하고, 무엇을 압축하고, 언제 다시 꺼낼지의 설계 문제다.
tags:
- long-context
- memory
- attention
- context-engineering
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

# 긴 컨텍스트와 메모리 관리

## 핵심 요약

긴 컨텍스트 문제는 "입력을 더 많이 넣기"가 아니라 **무엇을 보존하고, 무엇을 압축하고, 언제 다시 꺼낼지**의 설계 문제다. Transformer-XL은 이전 세그먼트 상태를 재사용하고, Longformer는 희소 어텐션으로 긴 문서를 선형 비용에 가깝게 처리하며, Infini-attention은 오래된 KV를 고정 크기 압축 메모리에 누적한다.

## 작동 원리

### 1. 순환 메모리로 컨텍스트 단절을 줄인다

Transformer-XL은 이전 세그먼트의 hidden state를 캐싱해 다음 세그먼트에서 재사용한다. 절대 위치 인코딩 대신 상대 위치 인코딩을 써서 세그먼트를 넘어도 시간적 일관성을 유지한다. 제품 관점에서는 긴 대화나 장문 문서 처리에서 "이전 문맥을 완전히 잊지 않는" 기본 구조다.

### 2. 희소 어텐션으로 계산량을 줄인다

Longformer는 모든 토큰이 모든 토큰을 보는 O(n²) self-attention 대신 sliding window, dilated window, task-specific global attention을 조합한다. 긴 문서 QA나 분류처럼 문서 전체를 다뤄야 하지만 모든 토큰 쌍을 볼 필요는 없는 작업에서 비용을 낮춘다.

### 3. 오래된 KV를 압축 메모리에 저장한다

Infini-attention은 오래된 KV를 버리지 않고 고정 크기 메모리 행렬에 압축 저장한다. 한 블록 안에서 지역 어텐션과 장기 메모리 어텐션을 결합해 입력 길이가 늘어도 메모리 사용량이 통제되도록 한다. 이 접근은 [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)의 "컨텍스트 압축"을 모델 내부 구조로 끌어온다.

## 활용 사례

- 긴 회의록/리서치 문서: 세부 조항은 local attention, 전체 요약은 압축 메모리나 계층 요약으로 처리한다.
- 장기 실행 에이전트: 모든 로그를 프롬프트에 다시 넣지 않고 상태, 결정, 실패 패턴만 승격한다.
- 엔터프라이즈 RAG: 원문 청크, 요약 노드, 메타데이터, 그래프 관계를 목적별 retrieval unit으로 분리한다.
- 개인 LLM Wiki: raw 전체가 아니라 wiki 페이지와 distill queue로 컨텍스트를 재사용한다.

## habix/강의와의 연결점

AI Human Ch08/Ch09에서 긴 컨텍스트는 모델 스펙 표로만 설명하면 약하다. 수강생에게는 세 가지 질문으로 설명하는 편이 낫다: "어떤 정보를 그대로 둘 것인가?", "무엇을 요약·압축할 것인가?", "언제 외부 메모리/RAG로 다시 가져올 것인가?" 이 질문이 [context-dealer-pattern](/concepts/context-dealer-pattern.md)과 [rag-architecture-optimization](/concepts/rag-architecture-optimization.md)으로 이어진다.

## 관련 개념

- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- [rag-architecture-optimization](/concepts/rag-architecture-optimization.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
- ai-paper-learning-path
