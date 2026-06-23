---
type: concept
title: 모델 라우팅과 비용 최적화
description: 에이전트 시스템 운영에서 모델 선택 기준이 "벤치마크 순위"에서 "1달러당 성능" 으로 이동하고 있다.
tags:
- model-routing
- cost-optimization
- per-dollar-performance
- agent-pricing
timestamp: '2026-06-23'
x-llmbrain-domain:
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 모델 라우팅과 비용 최적화

## 핵심 요약

에이전트 시스템 운영에서 모델 선택 기준이 "벤치마크 순위"에서 **"1달러당 성능"** 으로 이동하고 있다. 모델은 전구가 아니라 연료 — 매 호출마다 소비된다. 작업 유형에 따라 최적 모델을 배정하는 **라우팅 설계**가 PM의 새 레버리지다.

## 상세 내용

### 모델 선택 기준 전환 배경 (raw 원문 기준)

- Gemini 3.1 Pro: 16개 주요 벤치마크 중 13개 1위, 가격 $2/M 토큰 (GPT-5.4 대비 2/3 수준)
- Google TurboQuant: KV-Cache 압축으로 동일 품질을 **1/6 비용**으로 달성
- DeepSeek V4 Flash: 오픈소스, 400K 컨텍스트 + 추론 모드 동시 지원
- Anthropic 내부 전략: Opus 4.7은 복잡한 판단에만 투입, 일반 실행은 저비용 모델 담당 → **"가장 비싼 모델을 만드는 회사가 스스로 항상 최고 모델을 쓰지 말라고 자사 제품 운영 전략에 명시"**

### 3축 라우팅 설계 (raw 원문 기준)

#### 1축: 추론 복잡도

에이전트 시스템 호출에서 실제로 복잡한 멀티스텝 추론이 필요한 작업은 전체의 **10~20%**. 나머지 80~90%는 분류, 요약, 정보 추출, 반복 도구 호출.

- Step 3.5 Flash: 도구 호출 벤치마크에서 상위 모델과 대등, 비용은 **50배** 저렴
- GLM 5.1: Opus 제외 최고 수준 에이전틱 벤치마크, 비용 **1/3**

#### 2축: 모달리티

- 텍스트 전용 파이프라인 vs 이미지·영상 개입 파이프라인은 최적 모델이 다르다
- Gemini 3.1 Pro: 텍스트·이미지·오디오·비디오 단일 모델 처리, 할루시네이션 30% 감소
- 핵심 질문: "이 작업이 진짜 멀티모달인가, 아니면 텍스트 파이프라인에 이미지 전처리 하나가 붙은 것인가?"

#### 3축: 지연(Latency)

- Gemini 3.1 Flash Live: 음성·영상 실시간 처리 0.5초 이하, 기존 Flash 대비 30% 저렴
- 야간 배치, 보고서 생성 등 지연 요구 없는 작업에 실시간 고성능 모델을 쓰면 불필요한 비용
- **지연 × 추론 복잡도 2×2 매트릭스**로 작업 분류 후 각 사분면에 모델 배정

### 라우팅 함정 2가지 (raw 원문 기준)

**함정 1: 모든 작업에 최고 모델** — 파일럿에서 스케일로 넘어갈 때 비용 폭탄으로 드러난다.

**함정 2: 구버전 기준으로 저비용 모델 고정** — Karpathy: "AI capability gap = recency × tier of use". 모델 벤치마크는 매 분기 크게 바뀐다. 라우팅 설계는 한 번 결정하고 굳히는 게 아니라 **분기마다 재검증하는 운영 루틴**이 필요하다.

실전 결과: 사이냅소프트는 OCR 파이프라인에 벡터 양자화 적용으로 LLM 운영 비용 **70% 절감** — 최신 모델 교체가 아닌 작업 재분류 + 라우팅 최적화 결과.

### 100 Agents 프로젝트 실제 라우팅 기준 (raw 원문 기준)

| 노드 유형 | 사용 모델 |
|-----------|-----------|
| 복잡한 판단 (에이전트 간 조율, 멀티스텝 추론, 사용자 대면 핵심 응답) | Claude Opus 4.7 또는 GPT-5.5 |
| 반복 실행 (도구 호출, 분류, 요약, 배치 처리) | GLM 5.1 또는 DeepSeek V4 Flash |
| 멀티모달 개입 | Gemini 3.1 Pro |
| 실시간 음성 인터랙션 | Gemini 3.1 Flash Live |

### PM의 역할

라우팅 설계는 엔지니어링 문제이기 전에 **제품 설계 문제**다. 어떤 작업이 복잡한 추론이 필요한지, 어디서 사용자 지연이 경험 품질을 결정하는지, 어떤 파이프라인이 비용 누수인지 — 이것은 모델 스펙이 아니라 제품 워크로드 분석에서 나온다. PM이 이 분류 없이 엔지니어에게 "좋은 모델 써주세요"만 전달하면 전 노드에 최고 모델이 배정된다.

### 팀별 스코어카드와 라우팅 검증

2026-05-18 eval 설계 글의 보강: 글로벌 리더보드나 공급업체 벤치마크는 실제 업무 성과를 직접 예측하지 못한다. 모델 라우팅은 “우리 팀의 실제 작업 5개”에서 측정한 통과율로 검증해야 한다.

예시 작업: 고객 문의 분류, 내부 보고서 요약, 코드 리뷰, 법무 검토 초안, 데이터 정합성 확인. 각 작업의 성공 기준과 사람 검토 샘플 수를 고정해야 모델 교체와 라우팅 변경이 감으로 흐르지 않는다.

### 2026-05-19 보강: 에이전틱 완주율이 1차 지표가 됨

OpenAI flagship이 채팅 모델보다 agent runtime으로 포지셔닝되면서, 모델 선택 기준은 다시 한 번 바뀐다. raw 성능보다 중요한 것은 **에이전틱 완주율(task completion rate)** 이다. 긴 작업을 계획하고, 도구를 호출하고, 실패 후 복구하고, 최종 산출물까지 닫는 능력이 제품 지표가 된다.

라우팅도 “범용 모델 하나”가 아니라 작업 유형별 배정으로 가야 한다.

- 긴 계획·도구 사용·복구가 필요한 작업: agentic completion score가 높은 모델
- 단순 추출·분류·요약: 저비용 fast model
- 사용자 대면 최종 답변: latency와 tone 품질을 함께 보는 모델

따라서 비용/성능도 단순 벤치마크 점수가 아니라 **비용/에이전틱 점수**로 계산해야 한다. 에이전트가 중간에 멈추면 싸게 호출해도 실제 비용은 재시도·검수·사람 개입으로 올라간다.

### 2026-05-26 보강: Perplexity Computer의 20모델 오케스트레이션

Perplexity Computer Enterprise는 Slack, Snowflake, Datadog, Salesforce, SharePoint, HubSpot 커넥터를 붙이고 백엔드에서 20개 LLM을 동시에 오케스트레이션한다. 이 사례는 모델 라우팅이 비용 절감만이 아니라 **엔터프라이즈 커넥터별 작업 품질 관리** 문제라는 점을 보여준다.

음성 에이전트 관점에서도 구조는 같다. STT → 의도 파악 → 도구 호출(MCP) → 응답 생성 → TTS 단계마다 최적 모델과 latency budget이 다르다. 하나의 최고 모델이 아니라, 단계별 라우팅과 실패 시 fallback이 제품 품질을 만든다.

### 2026-05-31 보강: 개인 모델 티어와 context efficiency

CoolDeep의 Claude 온보딩은 개인 사용 레벨에서도 모델 라우팅을 Haiku, Sonnet, Opus로 나눈다. Haiku는 노트 요약·데이터 처리·단순 반복, Sonnet은 일상 업무, Opus는 깊은 분석·패턴 파악·복잡한 추론이다. 엔터프라이즈뿐 아니라 개인 워크플로우에서도 "최고 모델 하나"보다 작업 유형별 tiering이 기본값이 된다.

NLP Newsletter의 Efficiency Frontier는 context 비용이 production LLM bill의 큰 비중이라는 점을 다시 확인한다. deployment-aware optimization은 task performance, token cost, reuse를 함께 봐야 하며, 5,000개 HotpotQA instance에서 effective token usage를 약 25% 줄였고 amortized memory compression은 full-context 대비 50% 이상 낮은 token cost를 보였다. 라우팅의 다음 단위는 모델뿐 아니라 **얼마나 많은 컨텍스트를 어떤 형태로 재사용할 것인가**다.

Byte의 2026-05-31 경제 브리프는 한국 시장에서 반도체 섹터만 강하고, TSMC·Nvidia 대규모 투자 약속이 AI 인프라 경쟁을 밀어 올린다는 신호를 덧붙인다. 모델 라우팅 비용은 API 가격표만의 문제가 아니라 GPU/반도체 공급망과 capex 사이클에 노출된 운영 변수다.

### 2026-06-05 보강: Qwen3.7-Max와 서버리스 GPU가 라우팅 기준을 넓힌다

The Batch raw의 Qwen3.7-Max는 텍스트 전용 플래그십으로 1M 입력, 64K 출력, 208 tokens/sec, OpenAI/Anthropic API 호환, 낮은 hallucination률을 내세운다. 가격은 입력/캐시/출력 $2.50/$0.25/$7.50 per M tokens로, 긴 컨텍스트와 캐시 활용이 중요한 워크로드에서 별도 라우팅 후보가 된다. 단 응답 거부율이 높다는 신호는 safety-accuracy tradeoff를 팀별 scorecard에서 따로 봐야 함을 뜻한다.

Modal Labs의 서버리스 GPU 사례는 모델 라우팅이 API 모델 선택만이 아니라 **컴퓨트 시작 시간과 인프라 state reuse**까지 포함한다는 점을 보여준다. 같은 모델이라도 cold start가 50초인지 5초인지, 모델 메모리 상태를 복원할 수 있는지에 따라 사용자 대면/배치/백그라운드 에이전트 배치가 달라진다.

### 2026-06-09 보강: OS-level hybrid routing과 planning 전용 고급 모델

AI Human Day 69의 Apple Siri raw는 대형 플랫폼이 자체 모델과 외부 Gemini를 섞어 쓰는 OS-level hybrid routing 사례다. Siri가 모든 작업을 한 모델로 처리하지 않고, 내부 모델이 부족한 구간을 외부 LLM으로 보강한다면 라우팅 정책의 질문은 더 구체화된다: 어떤 데이터는 기기 안에 남기고, 어떤 작업은 자체 서버에서 처리하며, 어떤 추론만 외부 모델로 보낼 것인가.

Lenny의 Claude Fable 5 리뷰 raw는 최고급 모델도 모든 단계에 쓰기보다 planning layer로 배치하는 편이 맞다는 신호다. Fable 5는 깊은 reasoning과 제품 그래프/스킬 레지스트리 설계에서는 강하지만, 실행 단계에서는 보수적 확인 요청이 많고 토큰 소비가 크다고 기록됐다. 따라서 고가 Mythos-class 모델은 "긴 계획·아키텍처 설계·평가 기준 수립"에 라우팅하고, 반복 실행·파일 변경·단순 추출은 더 저렴하고 행동성이 높은 모델이나 하위 에이전트에 넘기는 구조가 비용/완주율 양쪽에서 낫다.

### 2026-06-11 보강: 구독 시대에서 사용량 예산 시대로

AI Human Day 70과 Axios raw는 모델 비용이 다시 제품 설계의 전면으로 올라왔다는 신호다. iOS 27의 "두뇌 모델 선택"은 사용자가 ChatGPT·Gemini·Claude 중 기본 모델을 고르는 OS-level 라우팅 사례이고, 토큰 단가는 GPT-5.5/Gemini 3.5 Flash $1.5/$9, Claude Opus 4.8 $5/$25, Grok 4.3 $0.5/$2처럼 모델별 격차가 커진다(raw 원문 기준). 사용자가 직접 고르게 하는 UX도 가능하지만, 제품 운영자는 기본값·fallback·민감 데이터 경로를 여전히 설계해야 한다.

Fable 5는 비용 구조 전환을 더 선명하게 만든다. 6월 22일까지는 구독 플랜에서 무료 제공되지만 6월 23일부터는 구독료 위에 usage credits가 별도로 필요하고, 가격은 Opus 모델의 2배로 기록됐다. 고성능 모델의 "작업당 비용이 낮다"는 주장은 가능한 주장일 뿐, 실제로는 내 작업에서 재시도 횟수, 검토 시간, 토큰 소비량, 완료율을 같이 측정해야 한다.

Pragmatic Engineer raw의 Uber 사례는 엔지니어링 조직에서 AI 예산이 headcount와 비교되는 단계로 들어왔음을 보여준다. 일부 기업은 per-engineer 월 예산 상한을 두고, 복잡한 작업만 frontier 모델로 올리는 smart model routing을 도입한다. 따라서 라우팅 정책의 운영 단위는 이제 "모델별 품질"이 아니라 팀별 월 예산, 워크로드별 intelligence premium, 비용 초과 시 degradation path까지 포함한다.

Huryn의 Fable 5 effort dial 실험은 같은 모델 안에서도 라우팅이 필요함을 보여준다. 단순 질문에는 max effort가 불필요한 지연과 편차를 만들 수 있고, 파일 간 모순 해결처럼 복잡한 작업에서는 xhigh 이상부터 의미 있는 차이가 나타났다(raw 원문 기준). 실무 기본값은 high, max는 드문 고위험 추론에만 쓰는 식의 effort routing이 모델 routing만큼 중요해진다.

### 2026-06-22 보강: 컴퓨트 제약과 워크플로우 과금

Axios의 데이터센터 모라토리엄 신호는 AI 비용이 단순 API 청구서를 넘어 지역 사회, 전력, 규제 리스크로 확장됐음을 보여준다. 신규 데이터센터 건설에 대한 유보 여론이 커지면 모델 라우팅과 컨텍스트 압축은 비용 절감이 아니라 제품 지속가능성과 공급 안정성의 문제다.

Roko의 workflow pricing 신호도 중요하다. 에이전트가 한 명의 좌석 보조가 아니라 5명분의 워크플로우를 실행한다면 순수 seat pricing은 가치 포착에 맞지 않는다. Runway Agent, Devin, 고객지원 에이전트처럼 전체 태스크를 닫는 제품은 사용량, 완료 결과, workflow package 기반 과금으로 이동할 가능성이 높다.

2026-06-12 양자화 논문 세트는 이 비용 문제의 모델 내부 해법이다. LLM.int8(), AWQ, QuaRot은 모델 호출 라우팅 이전에 "같은 모델을 얼마의 메모리와 지연으로 서빙할 것인가"를 바꾼다. 제품 레벨에서는 frontier API, 양자화 local model, batch/offline model을 workload별로 나누는 2단 라우팅이 필요하다.

## 관련 개념

- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [agent-pricing-model](/concepts/agent-pricing-model.md)
- [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)
- 260515_100_agents
- claude-code-workflow
- [llm-quantization-compression](/concepts/llm-quantization-compression.md)
