---
type: concept
title: Context-first 에이전트 오케스트레이션
description: 에이전트 시스템의 성패는 모델 성능이 아니라 컨텍스트 설계가 결정한다.
tags:
- context-first
- agent-orchestration
- mcp
timestamp: '2026-06-23'
x-llmbrain-domain:
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Context-first 에이전트 오케스트레이션

## 핵심 요약

에이전트 시스템의 성패는 모델 성능이 아니라 **컨텍스트 설계**가 결정한다. ServiceNow(Context Engine), Grok 4.20(역할별 병렬 검증), OpenAI Codex Chronicle(자동 메모리 축적), Snowflake Horizon Context + Cortex Sense — 서로 다른 세 곳이 같은 결론에 도달했다. Google Cloud Trends 2026: "워크플로우 > 모델."

## 상세 내용

### 왜 컨텍스트가 1차 변수인가 (raw 원문 기준)

에이전트 시스템 실패 원인 분석:
- 모델 환각 → 표면
- 잘못된 도구 선택 → 더 깊은 층
- **컨텍스트 없이 추론을 시작한 것** → 근본 원인

컨텍스트가 없거나 잘못 설계되면:
- 의도가 없으면 경계가 없다
- 경계가 없으면 루프가 생긴다
- 루프가 생기면 비용이 폭발한다

Karpathy (Sequoia Ascent 2026): "outsource thinking but not understanding" — 실행은 에이전트에 위임할 수 있어도 이해는 인간이 쥐고 있어야 한다. 그 '이해'가 에이전트에게 전달되는 방식이 컨텍스트 레이어다.

### 세 가지 레퍼런스 사례 (raw 원문 기준)

| 사례 | 방식 | 결과 |
|------|------|------|
| ServiceNow | "사이드카" → Context Engine 전환 | 기업 맥락을 에이전트의 출발점으로 |
| Grok 4.20 | 조정·팩트체크·논리·창의 에이전트 4개 병렬 검증 | 환각률 **65% 감소** |
| OpenAI Codex Chronicle | 사용자 화면 활동 자동 컨텍스트 축적 | 매 작업 재설명 불필요 |

업스테이지 × 다음(AXZ) 인수: Solar LLM + 20년치 한국어 검색 DB 결합. 업스테이지가 직접 붙인 키워드: **"context AI"**. 한국 시장 최초 Context-first 전략 선언.

Ethan Mollick 146개 경제팀 실험: Claude Code + Codex 에이전트 팀이 인간 중간값에 근접한 성과, **편차는 인간보다 훨씬 좁음**. 에이전트 AI의 진짜 가치 = "최고 성능"이 아닌 "좁은 편차의 일관된 양질".

### Context-first 설계 패턴 3가지 (raw 원문 기준)

#### 패턴 1: 컨텍스트 압축 — 필요한 것만 넘긴다

MCP context-mode: 에이전트 시스템 토큰 비용 **98% 감축** 오픈소스 서버.

```python
# 나쁜 예
context = load_entire_knowledge_base()  # 수백만 토큰, 비용 폭발

# 좋은 예
context = retrieve_relevant_context(task=current_task, top_k=5)  # 수백 토큰, 비용 통제
```

#### 패턴 2: 역할별 컨텍스트 분리 — 에이전트마다 다른 렌즈를 준다

하나의 에이전트가 모든 것을 알 필요가 없다. 적절한 역할의 에이전트가 적절한 컨텍스트로 검증하는 구조가 단일 강력한 에이전트보다 강하다. 에이전트 팀 성능은 개별 에이전트 지능보다 **역할과 컨텍스트 핸드오프 설계**에서 결정된다.

#### 패턴 3: 지속 메모리 레이어 — 매번 재설명하지 않는다

메모리를 "저장소"가 아닌 **"컨텍스트 재사용 레이어"** 로 보는 관점. 좋은 에이전트는 새 대화를 시작할 때도 이전 컨텍스트에서 출발한다.

### Context-first 설계의 핵심 질문

> "이 에이전트는 작업 시작 시 어떤 컨텍스트를 받는가?"

이 질문에 명확히 답할 수 있으면 Context-first 설계를 하고 있는 것. 답하기 어렵다면 "일단 다 넘기자" 접근을 하고 있을 가능성이 높다.

### 2026-05-20 보강: 관찰 메모리와 컨텍스트 승격

에이전트 메모리는 별도 저장소가 아니라 아키텍처다. raw/blog/2026-05-20의 핵심 문장은 “Memory is not a layer. Memory is the architecture.”다. 중요한 설계 질문도 “무엇을 기억할까”보다 먼저 **언제 무엇을 컨텍스트에 올릴까**로 바뀐다.

메모리는 3층으로 나뉜다.

1. **관찰 메모리**: 사용자의 반복 행동, 선호, 작업 패턴을 누적한다.
2. **작업 메모리**: 현재 태스크의 목표, 제약, 진행 상태를 유지한다.
3. **승격 메모리**: 반복 검증된 패턴만 장기 규칙으로 올린다.

소유권이 없는 메모리는 잡음이 된다. 누가 기록하고, 누가 승격하고, 누가 폐기하는지 정하지 않으면 에이전트는 오래될수록 똑똑해지는 대신 과거 맥락에 오염된다.

### 2026-06-02 보강: AI-native engineering과 Product Navigator

ByteByteGo의 AI-native engineer 가이드는 컨텍스트 설계를 엔지니어 핵심 역량으로 명시했다. AI가 코드의 75% 이상을 작성하는 환경에서 병목은 타이핑 속도가 아니라 **Context Engineering, Spec-Driven Development, Critical Verification, Disciplined Problem Decomposition**이다. 즉 좋은 엔지니어는 코드를 직접 쓰는 사람에서 에이전트가 다룰 수 있는 문제 단위, 제약 조건, 검증 기준을 설계하는 오케스트레이터로 이동한다.

Cerebral Valley의 Brief 사례는 같은 문제를 제품 맥락에서 푼다. Brief는 GitHub, Notion, Linear, Granola 같은 비즈니스 시스템을 읽어 Product Graph를 만들고, Claude Code/Cursor/Codex가 제품 결정사항과 페르소나를 물어볼 수 있게 한다. Dark Factory 실험에서 Brief 없는 자율 코딩은 46%, Brief 있는 경우 95% 올바른 솔루션에 도달했다는 신호는 모델 성능보다 제품 컨텍스트 주입이 더 큰 레버일 수 있음을 보여준다.

Cool Deep AI의 슬래시 커맨드 raw와 AI Human의 CLAUDE.md 사례는 가장 작은 단위의 컨텍스트 재사용 패턴이다. 반복 페르소나·톤·제약 조건을 매 세션 타이핑하지 않고 slash command나 `CLAUDE.md`로 고정하면, 에이전트는 매번 같은 규칙을 재발견하지 않는다. 이 흐름은 [260515_llm_wiki](/projects/260515_llm_wiki.md)의 raw→wiki 컴파일 구조와도 같다. 반복되는 맥락은 대화창에 남기는 것이 아니라 재사용 가능한 파일/도구로 승격해야 한다.

### 2026-06-09 보강: Agentforce 20,000개 배포와 workflow redesign

ByteByteGo의 Salesforce Agentforce 20,000개 기업 배포 요약은 컨텍스트 설계를 더 운영적인 4계층으로 정리한다. Engagement Layer는 Slack/chat 같은 일상 인터페이스, Agent Layer는 추론·의사결정·모니터링, System of Work는 실제 업무 앱, Context Layer는 데이터·메타데이터를 공급한다. Trust Layer는 이 전체를 가로질러 다중 LLM, 가드레일, 정책을 적용한다.

핵심 발견은 "데모 이후 무슨 일이 일어나는지 모르는 에이전트"가 실패한다는 점이다. 일반 LLM 호출만 붙인 에이전트는 제품 데모에서는 그럴듯하지만, 지원 케이스 해결·반품 처리·영업 파이프라인 업데이트처럼 실제 업무 시스템에 쓰기 시작하면 맥락과 권한 경계가 없어서 무너진다. 반대로 성공한 에이전트는 System of Work에 깊이 들어가 있고, Context Layer가 비즈니스 상태를 계속 공급한다.

McKinsey의 Sonar 사례도 같은 결론이다. AI를 소프트웨어 개발에 "도구 하나 추가"로 붙이면 가치의 일부만 얻고, planning → coding → review → deployment 전체 워크플로우를 다시 설계할 때 속도·품질·확장성의 step-change가 나온다. 따라서 context-first는 프롬프트 작성 기법이 아니라 업무 레이어, 시스템 레이어, 신뢰 레이어를 재배치하는 운영 아키텍처다.

### 2026-06-10 보강: 살아있는 업무 맥락과 컨텍스트 압축

a16z raw의 "Everything is Recorded Now"는 기업 내 맥락 레이어가 문서보다 미팅 녹음에서 만들어지는 흐름을 기록한다. 신입 직원이 위키만 읽고 온보딩되지 않고 회의에 참여해 문화·기대치·예외 처리를 배우듯, AI도 모든 미팅에 동시 참석하며 구두 맥락을 구조화한다. Granola 같은 미팅 기록 도구가 회사의 실제 사고 방식과 의사결정 흐름을 가장 잘 아는 시스템이 되는 이유다.

이 흐름은 context-first의 메모리 레이어를 바꾼다. 시스템 오브 레코드가 CRM·티켓·문서 같은 구조화 데이터에 머물렀다면, 다음 레이어는 고객 콜의 뉘앙스, 제품 리뷰의 논쟁, 리더십 미팅의 즉흥적 방향 전환 같은 비정형 대화다. 기본값은 opt-in 녹음에서 "민감 미팅만 명시적 제외"로 이동할 수 있으며, HR·법무 같은 영역에는 별도 접근 레벨과 보존 정책이 필요하다.

CatchPaper의 Meta LCLM 신호는 긴 컨텍스트 운영의 비용 해법을 보여준다. Latent Context Language Model은 긴 문맥을 latent embedding으로 end-to-end 압축해 KV cache 메모리와 latency를 줄인다(raw 원문 기준 16배 압축). 제품 관점에서는 "모든 컨텍스트를 그대로 넣기"가 아니라 훑어보고 압축한 뒤 필요한 부분만 확대하는 계층적 컨텍스트 접근이 중요해진다.

McKinsey adoption/scaling raw와 Linear coding sessions는 context-first가 도입 이후 확산 설계까지 포함함을 보여준다. AI coding session이 issue, customer request, history, discussion, related work를 읽고 diff를 내는 구조는 컨텍스트가 따로 검색되는 자료가 아니라 작업 표면 안에 미리 접착된 상태다. Adoption과 scaling은 사후 교육이 아니라 upstream 구현과 downstream 조직 변화가 함께 설계될 때 작동한다.

### 2026-06-18 보강: 선언형 컨텍스트와 자동 수집 컨텍스트의 분리

AI Human Day 76의 Snowflake Horizon Context + Cortex Sense 신호는 엔터프라이즈 컨텍스트 레이어를 두 층으로 나눈다. Horizon Context는 팀이 직접 선언·큐레이션하는 비즈니스 로직, 지표 정의, 용어 의미를 맡고, Cortex Sense는 플랫폼이 자동으로 수집하는 사용 패턴과 데이터 맥락을 맡는다. 두 레이어가 Cortex Search 같은 RAG 흐름에 합쳐질 때 에이전트는 단순 문서 검색이 아니라 업무 의미론 위에서 답하게 된다.

이 사례가 중요한 이유는 "자신 있는 오답"을 모델 환각 하나로 보지 않는다는 점이다. 모델이 틀린 답을 자신 있게 내놓는 근본 원인은 종종 최신 데이터 부족보다 **비즈니스 의미와 정책 정의가 컨텍스트로 들어오지 않은 것**이다. 따라서 context-first 설계에서는 prompt, retrieval, semantic layer, policy layer를 한 덩어리로 보지 말고, 사람이 책임지는 선언형 컨텍스트와 시스템이 관찰하는 자동 컨텍스트를 분리해 관리해야 한다.

같은 날짜의 Memory/Long-Context 논문 세트도 이를 구조적으로 뒷받침한다. Transformer-XL은 이전 세그먼트 상태를 메모리로 재사용하고, Longformer는 희소 어텐션으로 긴 문서를 선형 비용에 가깝게 처리하며, Infini-attention은 오래된 KV를 압축 메모리에 누적한다. 제품 관점에서는 "컨텍스트를 무한히 넣는다"보다 **무엇을 보존하고, 무엇을 압축하고, 어떤 순간에 다시 올릴지**를 정하는 것이 핵심이다.

### 2026-06-19 보강: 멀티 LLM과 영구 프로젝트 메모리

AI Human Day 77의 Upstage Company/TimelyAI 신호는 context-first가 단일 모델 내부 최적화가 아니라 **여러 모델을 바꿔 끼우는 운영 계층**이 되어야 함을 보여준다. 70개 이상 LLM을 단일 플랫폼에서 쓰는 환경에서는 프롬프트 자체보다 작업 컨텍스트, 출력 계약, 모델별 차이를 재현 가능하게 비교하는 eval harness가 중요해진다.

CoolDeep의 Claude Projects raw는 같은 원칙을 개인 워크스페이스 단위로 보여준다. Projects는 문서, 맞춤 지침, 파일을 한 곳에 두고 모든 대화가 그 영구 컨텍스트에서 시작하게 만든다. 이는 "매번 설명하기"를 멈추고 반복 업무의 브랜드 보이스, 고객 맥락, 작업 절차를 컨텍스트 레이어로 승격하는 패턴이다. Claude Code/Cowork에서는 이 역할을 `CLAUDE.md`, `MEMORY.md`, Resources 폴더, Skills가 나눠 맡는다.

### 2026-06-20 보강: 기술과 업무 연결이 모델보다 먼저다

AI Human Day 77의 CIS 2026 신호는 엔터프라이즈 에이전트 성과의 병목을 모델 성능이 아니라 **기술과 업무 시스템의 연결 부족**으로 본다. 에이전트가 실제 업무에서 가치를 내려면 CRM, 포털, 문서, 승인 흐름, 검색 레이어가 어떤 의미와 권한으로 연결되는지 먼저 정리되어야 한다.

이는 Ch07 system prompt와 Ch08 context engineering의 경계도 선명하게 만든다. 시스템 프롬프트는 역할과 제약을 고정하고, 컨텍스트 레이어는 작업 순간 필요한 업무 의미·근거·상태를 공급한다. Ch09 [rag-architecture-optimization](/concepts/rag-architecture-optimization.md)로 넘어가면 이 컨텍스트 공급은 retriever, reranker, semantic layer, corrective loop의 문제로 구체화된다.

### 2026-06-22 보강: Workflow가 제품이 되는 시점

AI Human Day 79의 deepagents, AWS enterprise agent platform, Salesforce Fin 인수, KAIST 옴니RAG/아카식DB 신호는 에이전트 제품의 경쟁 축이 모델 호출에서 **업무 흐름 전체를 붙잡는 플랫폼**으로 이동했음을 보여준다. "배터리 포함" 하네스, 오케스트레이션 기본 탑재, 고객서비스 에이전트 인수는 모두 같은 방향이다. 사용자는 챗봇을 원하는 것이 아니라 특정 업무가 끝까지 완료되는 흐름을 원한다.

Roko의 "workflow is the product" 글은 이 방향을 더 선명하게 표현한다. Runway Agent는 스크립트 작성, 생성, 편집, 음향까지 영상 프로덕션 파이프라인을 한 대화에서 처리한다. Devin 같은 코딩 에이전트, 엔터프라이즈 자동화, 고객지원 에이전트도 동일하다. 보조 기능이 아니라 workflow 소유권이 가치 포착 지점이 된다.

ByteByteGo의 AI-native leaders playbook은 조직 구조도 이에 맞춰 바뀐다고 본다. 2~5명 AI-native pod와 전담 에이전트 세트, Agent Champion, PR cycle time/에이전트 생성 코드 비율/배포 빈도/보안 사고 같은 운영 지표가 등장한다. Context-first는 이제 개인 prompt skill이 아니라 팀 구조, 측정 지표, 보안 가드레일을 포함한 조직 운영 설계다.

NNGroup의 Vibe Architects 신호는 UX 과제를 덧붙인다. 에이전트 도구의 가장 큰 문제 중 하나는 "무엇을 만들 수 있는지"를 사용자가 이해하지 못한다는 점이다. 강력한 기능보다 온보딩, 예시, 커뮤니티 학습, 안전한 시작점이 adoption을 좌우한다.

## 관련 개념

- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
- claude-code-workflow
- 260515_100_agents
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [rag-architecture-optimization](/concepts/rag-architecture-optimization.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [agent-skill-optimization](/insights/agent-skill-optimization.md)
