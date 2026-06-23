---
type: concept
title: RAG 아키텍처와 최적화
description: RAG는 "검색한 청크를 프롬프트에 붙이는 기능"이 아니라 retriever와 generator를 분리해 각각 최적화하는 시스템이다.
tags:
- rag
- retrieval
- retriever-reader
- modular-rag
timestamp: '2026-06-22'
x-llmbrain-domain:
- AI/LLM
- Retrieval
x-llmbrain-created: '2026-06-21'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# RAG 아키텍처와 최적화

## 핵심 요약

RAG는 "검색한 청크를 프롬프트에 붙이는 기능"이 아니라 retriever와 generator를 분리해 각각 최적화하는 시스템이다. FiD는 여러 지문을 생성 단계에서 융합하는 reader 구조를, REPLUG는 폐쇄형 LLM 환경에서 retriever를 최적화하는 방식을, Modular RAG는 query rewriting, routing, reranking, 반복 검색을 모듈로 조립하는 설계 언어를 제공한다. 그 다음 단계의 Advanced RAG는 검색 품질을 평가·교정(CRAG), 검색 단위를 계층화(RAPTOR), 지식 구조를 그래프화하고 증분 갱신(LightRAG)하는 방향으로 확장된다.

## 작동 원리

### 1. Reader는 여러 근거를 융합한다

Fusion-in-Decoder(FiD)는 검색된 여러 passage를 인코더에서 각각 처리하고, 디코더가 cross-attention으로 한꺼번에 융합해 답을 생성한다. 중요한 직관은 검색 지문 수를 늘리면 답변 품질이 좋아질 수 있지만, 단순 concat이 아니라 "어디서 융합할 것인가"가 품질과 비용을 좌우한다는 점이다.

제품 관점에서는 top-k 청크 수, 청크 길이, 문서별 독립 인코딩, 최종 생성 단계의 근거 종합 방식이 모두 reader 설계 문제다. 이는 [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)에서 말하는 컨텍스트 공급 품질을 생성기 내부 구조까지 끌어내린다.

### 2. 폐쇄형 LLM에서는 retriever가 주된 최적화 레버다

REPLUG는 GPT/Claude 같은 블랙박스 LLM의 가중치를 건드릴 수 없을 때, 검색된 문서를 입력 앞에 붙이고 retriever만 LLM 출력 확률 기반 신호로 학습시키는 접근을 제안한다. 실무 RAG의 다수는 API-only 모델 위에 올라가므로, 모델 자체보다 "어떤 문서를 가져오면 LLM이 더 잘 맞히는가"를 측정하고 검색기를 개선하는 루프가 핵심이 된다.

이 관점은 agent-evaluation-frameworks와 직접 연결된다. RAG 평가도 검색 recall만 볼 것이 아니라, 문서가 실제 답변 정확도와 faithfulness를 올렸는지까지 봐야 한다.

### 3. 현대 RAG는 모듈식 워크플로우다

Modular RAG는 Naive RAG의 검색 -> 생성 선형 흐름을 넘어, RAG를 module, submodule, operator로 나눈다. 실제 프로덕션에서는 query rewriting, routing, reranking, fusion, adaptive retrieval, self-check, corrective loop가 조건부·분기형·반복형으로 조립된다.

따라서 좋은 RAG 설계 질문은 "어떤 벡터DB를 쓸까"보다 다음에 가깝다.

- 질문을 검색 가능한 형태로 다시 쓸 것인가?
- dense, sparse, multi-vector 검색을 어떻게 조합할 것인가?
- 검색 결과를 reranker나 LLM judge로 걸러낼 것인가?
- 답변 근거가 부족하면 재검색할 것인가?
- 실패를 어떤 eval로 감지하고 어느 모듈을 교체할 것인가?

### 4. 검색 실패를 그대로 믿지 않는다

CRAG(Corrective Retrieval Augmented Generation)는 검색 결과와 생성 사이에 retrieval evaluator를 둔다. 평가 결과가 충분하면 기존 검색 결과를 쓰고, 부족하면 웹 검색 같은 보조 지식원으로 보강하거나 답변을 보류한다. 핵심은 "검색했으니 근거가 있다"가 아니라 "검색 결과가 이 질문에 쓸 만한가"를 별도 단계에서 판정하는 것이다.

운영 관점에서는 hallucination 방어가 모델 프롬프트만의 문제가 아니게 된다. retriever confidence, reranker score, LLM judge, 답변 faithfulness eval을 묶어 retrieval quality gate를 만들고, 기준 미달 시 fallback·재검색·human handoff로 분기해야 한다. 이 패턴은 [agent-harness-pattern](/concepts/agent-harness-pattern.md)의 eval-gated loop와 같은 구조다.

### 5. 검색 단위는 평면 청크에 갇히지 않는다

RAPTOR는 문서를 청크로 쪼갠 뒤 그 청크들을 재귀적으로 클러스터링하고 요약해 트리 구조를 만든다. 하위 노드는 세부 사실, 상위 노드는 추상화된 요약을 담으므로, 질의 시 세부 근거와 전체 맥락을 함께 검색할 수 있다.

실무 의미는 크다. "이 계약서의 특정 조항은?" 같은 local query에는 원문 청크가 필요하지만, "이 보고서 전체의 리스크는?" 같은 global query에는 요약 노드가 더 적합하다. RAG 품질은 chunk size 하나로 끝나는 문제가 아니라, 원문·요약·그래프·메타데이터 중 어떤 retrieval unit을 노출할지의 설계 문제다.

### 6. 그래프 RAG는 운영 비용과 증분 갱신까지 봐야 한다

LightRAG는 GraphRAG의 엔티티·관계 구조를 활용하면서도 비용과 복잡도를 낮추려는 경량 프레임워크다. low-level entity retrieval과 high-level topic retrieval을 결합하고, 새 문서가 들어올 때 전체 인덱스를 다시 만들지 않는 incremental update를 강조한다.

이는 사내 위키, 제품 문서, 뉴스 피드처럼 계속 변하는 지식베이스에서 중요하다. 그래프 기반 검색이 강하더라도 매일 전체 인덱스를 재구축해야 한다면 운영 제품으로 쓰기 어렵다. 따라서 Advanced RAG 선택 기준에는 정확도뿐 아니라 indexing cost, update latency, graph freshness가 포함돼야 한다.

### 7. Dense retrieval은 negative와 하이브리드 구조가 품질을 가른다

2026-06-19 dense retrieval 논문 세트는 RAG의 검색 품질을 "어떤 임베딩 모델을 쓰나"보다 학습 데이터와 negative sampling 문제로 본다. ANCE는 ANN 인덱스에서 hard negative를 동적으로 샘플링해 실제 검색 환경의 어려운 오답을 구분하게 만들고, Contriever는 라벨 없이도 contrastive 사전학습으로 zero-shot retriever를 만든다.

BGE-M3는 이 흐름을 dense, sparse, multi-vector 검색을 한 모델에 통합하는 방향으로 확장한다. 한국어/영어 혼합 사내 문서나 긴 문서 RAG에서는 단일 dense vector만으로 충분하지 않을 수 있다. dense recall, sparse keyword precision, multi-vector late interaction을 score fusion으로 조합하는 하이브리드 검색이 기본값에 가까워진다.

### 8. 벡터DB는 압축과 인덱스 구조의 결합이다

2026-06-22 vector database 논문 세트는 대규모 벡터 검색을 압축과 인덱싱의 조합으로 설명한다. Product Quantization(PQ)은 벡터를 여러 부분공간으로 나눠 짧은 코드로 압축하고, SPANN은 centroid는 메모리에, posting list는 SSD에 두는 메모리-디스크 하이브리드 구조로 십억 규모 검색 비용을 낮춘다. RaBitQ는 1비트/차원 양자화와 오차 보증을 결합해 recall-cost tradeoff를 더 정량적으로 다룬다.

KAIST의 옴니RAG/아카식DB 신호는 이 기술 축이 제품 레이어에서는 벡터, 그래프, 관계형 DB의 통합으로 보인다는 점을 보여준다. 사용자는 "벡터 검색"을 원하는 것이 아니라 권한, 관계, 최신성, 의미 검색이 한 질의에서 함께 작동하기를 원한다.

## 활용 사례

- 멀티 문서 QA: FiD식으로 여러 문서를 독립적으로 읽고 생성 단계에서 종합한다.
- API-only RAG: REPLUG식으로 폐쇄형 LLM은 고정하고 retriever와 검색 평가 루프를 개선한다.
- 엔터프라이즈 지식검색: 권한, 최신성, 도메인 용어, semantic layer를 query routing과 reranking 모듈로 분리한다.
- LangGraph/LlamaIndex 파이프라인: linear, conditional, branching, looping 패턴으로 RAG 흐름을 명시적으로 표현한다.
- 고객 지원/사내 QA: CRAG식 품질 게이트로 검색 신뢰도가 낮을 때 답변 보류, 웹 검색 fallback, 담당자 handoff를 실행한다.
- 긴 문서/보고서 QA: RAPTOR식 계층 요약 노드로 문서 전체 질문과 세부 조항 질문을 다른 레벨에서 처리한다.
- 지속 갱신 지식베이스: LightRAG식 dual-level retrieval과 incremental update로 그래프 검색의 운영 비용을 낮춘다.
- 다국어 사내 검색: BGE-M3식 dense/sparse/multi-vector 통합으로 한국어·영어·긴 문서 검색을 함께 처리한다.
- 대규모 벡터 서빙: PQ, SPANN, RaBitQ 같은 압축·인덱싱 전략으로 RAM 비용과 latency를 통제한다.

## habix/강의와의 연결점

AI Human Module 9에서 RAG는 "벡터DB 실습"으로 시작하면 약하다. 먼저 FiD -> REPLUG -> Modular RAG 순서로 기본 뼈대를 잡고, 그 다음 CRAG -> RAPTOR -> LightRAG로 넘어가면 수강생은 RAG를 검색기, reader, 평가 루프, 오케스트레이션 모듈, 지식 구조의 조합으로 이해할 수 있다.

강의 메시지는 "검색을 붙이면 환각이 줄어든다"가 아니라 "검색된 근거가 실제로 답변 품질을 올리는지 측정하고, 부족하면 retriever나 workflow를 바꾼다"가 되어야 한다. 이 흐름은 ai-paper-learning-path Module 9와 [agent-harness-pattern](/concepts/agent-harness-pattern.md)의 eval-gated loop로 이어진다.

## 관련 개념

- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- agent-evaluation-frameworks
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- ai-paper-learning-path
- [prompt-engineering-as-system-design](/concepts/prompt-engineering-as-system-design.md)
- [long-context-memory-management](/concepts/long-context-memory-management.md)
