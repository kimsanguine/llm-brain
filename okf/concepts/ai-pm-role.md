---
type: concept
title: AI PM 역할 전환
description: AI 에이전트가 코드를 짜는 시대에 PM 역할은 줄어드는 게 아니라 병목 위치가 이동한다.
tags:
- ai-pm
- pm-paradigm
- agent-orchestration
- agent-evaluation
timestamp: '2026-06-06'
x-llmbrain-domain:
- AI/LLM
- teaching
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# AI PM 역할 전환

## 핵심 요약

AI 에이전트가 코드를 짜는 시대에 PM 역할은 줄어드는 게 아니라 **병목 위치가 이동**한다. "코드 생산"이 자동화될수록 "무엇을 만들지 결정하는 구조"와 "무엇을 성공으로 볼지 평가하는 기준"이 팀 성과를 더 크게 좌우한다. PM은 문서 작성자에서 에이전트 오케스트레이터·평가 설계자로 전환이 요구된다.

## 상세 내용

### 왜 지금인가 (raw 원문 기준)

- McKinsey 2024: 글로벌 기업 **72%**가 AI 기능을 비즈니스 프로세스에 도입 (전년 50%에서 급증)
- Gartner 2024: AI 도입 기업의 **63%**가 PoC 이후 내재화 실패 → 공통 원인: "AI를 이해하는 PM이 없어서"
- Andrew Ng: 에이전트 코딩 속도가 높아질수록 "무엇을 만들지 결정하는 역할"이 진짜 병목이 된다. [ai-education-evolution](/concepts/ai-education-evolution.md)이 보여주듯 AI 리터러시 격차가 PM 역할 변화를 가속한다.
- 삼성SDS AX센터 수치: 에이전트 실제 도입률 **5%** — 기술 파일럿은 넘쳤으나 실제 운영까지 간 경우는 20분의 1
- Andrew Ng 언급 엔지니어:PM 비율 변화: **8:1 → 1:1** — PM 자리가 줄어드는 게 아니라 PM 한 명이 팀 전체 방향의 핵심 결정자가 되는 구조

### PM 역할의 세 가지 변화

#### 1. 문서 작성자 → 오케스트레이터

전통 PM의 시간 구조:
- PRD 작성: 3~5일 / 데이터 분석 대기: 2~3일 / 경쟁사 리서치: 반나절~하루

AI 네이티브 PM은 이 시간 구조 자체를 바꾼다. PRD 초안 1시간, 데이터 분석은 CSV 즉시. 남은 시간을 더 높은 수준의 판단에 투입.

#### 2. 혼자 일하는 PM → AI 팀을 운영하는 PM

`.claude/agents/` 폴더에 에이전트를 정의하면 PM은 사실상 팀장이 된다. 인원이 늘어나는 게 아니라 **레버리지**가 늘어난다.

#### 3. 실행 의존 PM → 직접 빌드하는 PM

엔지니어에게 맥락을 전달하는 데 쓰던 에너지가 실제 제품을 검증하는 데 쓰인다.

### AI 네이티브 PM 레벨 (raw 원문 기준)

| 레벨 | 정의 | 핵심 역량 |
|------|------|-----------|
| **J (Junior)** | AI 도구를 쓸 수 있다 | ChatGPT 문서 작성, 기본 프롬프팅 |
| **P (Practitioner)** | AI 워크플로우를 설계한다 | Claude Code, CLAUDE.md, 슬래시 커맨드 |
| **L (Leader)** | AI 팀을 운영한다 | 멀티 에이전트, MCP 통합, 자동화 파이프라인 |

### 에이전트 시대 PM의 세 가지 전환 (raw 원문 기준)

#### 문서 작성자 → 평가 설계자

PRD를 잘 쓰는 것보다, 에이전트가 만든 결과물을 **어떻게 평가할지**가 더 중요해졌다. 평가를 설계하지 않으면 도구 도입 자체가 도박이 된다. [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)가 RLHF를 통해 보여준 "인간 선호 정렬"의 핵심도 결국 평가 기준을 어떻게 명시하느냐였다 — PM의 Eval 설계는 그 연장선이다.

> CLAUDE.md 도입 시 작업 시간 28% 감소 논문과 비용 20% 증가·정확도 하락 논문이 같은 시기에 나왔다 — 작업 유형에 따라 정반대 결과. PM이 작업 유형별 평가 기준을 설계해야 한다.

#### 기능 관리자 → 에이전트 오케스트레이터

에이전트 역할 정의, 실패 처리, 결재 구조를 설계하는 것이 PM의 일이다. [karpathy](/people/karpathy.md): "사고는 위임할 수 있어도, 이해는 위임할 수 없다."

#### 기술 지표 → 비즈니스 성과 측정

경영진이 보는 것은 정확도·벤치마크가 아니라 시간 절감, 비용 감소, 매출 기여. PM이 이 번역을 직접 해야 한다.

### PM이 지금 해야 할 것 (raw 원문 기준)

1. **평가 기준을 먼저 설계** — Spec 전에 Eval을 잡는다. "이 에이전트가 성공한 상태는 어떤 상태인가?"
2. **에이전트 팀의 의사결정 구조 설계** — 어떤 결정을 에이전트가 하고, 어떤 결정은 사람이 하는지 명확히
3. **ROI를 작업 단위로 측정** — 전체 생산성 향상이 아니라 작업 유형별로 분해

### 2026-05-14~17 보강: PM 레버리지의 세부 분화

- **에이전시**: 스킬은 AI가 따라잡지만 선택력·주도성·실행 책임은 PM에게 남는다. AI 출력물에는 반드시 “우리 상황에서의 의미”를 붙여 이해를 위임하지 않는다. 자세한 원칙은 [pm-agency-ai-era](/concepts/pm-agency-ai-era.md) 참조.
- **팀 의사결정 구조**: 코딩 속도가 올라가도 리뷰·권한·맥락 공유 병목은 남는다. PM의 1차 레버리지는 도구 선택이 아니라 의사결정 경계와 검증 구조 설계다. 자세한 구조는 [team-decision-structure-agent-era](/concepts/team-decision-structure-agent-era.md) 참조.
- **한 명의 N**: 백그라운드 에이전트 시대에는 사용자 한 명이 동시에 굴리는 에이전트 수가 새 KPI가 된다. N이 늘수록 검토 시간 예산과 human approval gate가 중요해진다. 자세한 지표는 [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) 참조.

### 2026-05-18 보강: Spec보다 Eval이 병목

원티드랩 PO의 “무엇을 성공으로 볼지 정의” 발언, LangChain CEO의 “2026 is the year of evals”, 아마존 내부 AI 코딩 도구의 통과율 미달 사례가 같은 방향을 가리킨다. AI 도구 도입의 병목은 모델 성능 자체보다 **팀 업무 기준으로 무엇을 통과로 볼지 설계하는 능력**이다.

PM의 평가 설계 실천은 세 가지로 압축된다.

1. **P0/P1/P2 게이트 정의**: 결제·인증·삭제 같은 P0 작업은 LLM-as-judge 점수가 높아도 사람 리뷰를 유지한다.
2. **팀별 스코어카드 작성**: 범용 벤치마크 대신 고객 문의 분류, 보고서 요약, 코드 리뷰 등 실제 업무 5개에서 모델별 통과율을 측정한다.
3. **자율성 경계 설정**: 에이전트가 스스로 결정 가능한 범위와 사람 개입 지점을 사전에 명시한다. 이해는 위임할 수 없다.

2026-05-28 Context Dealer 블로그는 같은 원칙을 더 짧게 압축한다. AI 제품 도입의 실패는 대개 모델 능력 부족이 아니라 맥락과 평가 기준 부족에서 나온다. PM의 새 역할은 기능 명세서를 먼저 쓰는 사람이 아니라, “무엇이 해결되면 성공인가”와 “어떻게 확인할 것인가”를 먼저 닫는 사람이다.

### 2026-05-21~25 보강: PM의 AI 워크플로우는 복리 구조다

AI를 “도구로 쓰는 것”과 “함께 성장하는 시스템으로 설계하는 것”은 다르다. 복리형 PM 워크플로우는 컨텍스트 축적, 취향 명시, 검증 자동화, 단계적 위임, 피드백 루프가 쌓일수록 성능이 오른다. 즉 PM의 새 일은 프롬프트를 잘 쓰는 것이 아니라 **반복될수록 좋아지는 작업 시스템**을 설계하는 것이다.

Andrew Ng의 팀별 AI 가속 관찰은 이 역할을 더 구체화한다. 프론트엔드는 빠르게 가속되지만, 백엔드는 검증 게이트가 먼저고, 인프라는 보조 도구에 머물며, 리서치는 가장 느리다. PM은 “AI 도입으로 모두 빨라진다”가 아니라 영역별 기대치와 검증 구조를 다르게 설계해야 한다. [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)는 이 영역별 분화를 인프라 관점에서 보여준다.

2026-05-25의 멀티 AI PM 워크플로우 신호도 같은 흐름이다. Codex와 Claude를 동시에 쓰는 PM은 도구를 번갈아 쓰는 사람이 아니라, 자율성 × 사용 환경에 따라 역할을 나누는 오케스트레이터다. 제품 판단, 구현, 리뷰, 문서화를 한 모델에 몰아주지 않고 모델 간 상호 검증 구조를 만든다. [demis-hassabis](/people/demis-hassabis.md)와 [geoffrey-hinton](/people/geoffrey-hinton.md), [yann-lecun](/people/yann-lecun.md)이 각자 다른 AI 미래를 그리듯, PM도 단일 모델에 의존하지 않는 오케스트레이션 관점이 필요하다.

### 2026-05-31 보강: AI 불안은 로드맵과 task/job 구분으로 다룬다

Delight Path 라운드테이블에서 Director·VP·Head of Product 40명 대부분이 AI 준비도를 3~4점으로 답했다. 중요한 신호는 시니어 PM들도 LinkedIn/VC Twitter의 과장된 속도감 때문에 뒤처졌다고 느낀다는 점이다. 대응은 모든 툴을 따라가는 것이 아니라, 같은 압박을 받는 실무자들과 대화하고 자기 학습 로드맵을 정한 뒤 나머지 소음을 버리는 것이다.

Benedict Evans의 "AI는 1997년 인터넷" 프레임도 PM에게 유용하다. 잘못된 질문은 "AI가 내 일의 몇 %를 할 수 있나"이고, 더 나은 질문은 "이것은 task인가, job인가"다. 일부 task가 자동화돼도 job은 재구성된다. 따라서 PM의 할 일은 도구 공포에 반응하는 것이 아니라, 업무를 task 단위로 분해하고 어떤 판단·책임·분배 우위가 남는지 설계하는 것이다.

Josh Pigford 사례는 이 전환의 실전 버전이다. 25년 경력 솔로 빌더가 에이전트 스킬 스택으로 5개 제품을 동시에 운영한다. PM 관점의 메시지는 "기술 경험이 없어도 된다"보다 더 좁다. 빠른 출시, 교차 검증, 학습 루프, 반복 스킬화가 있으면 1인이 다제품 운영을 설계할 수 있다.

### 2026-06-05 보강: PM은 살아있는 가정을 공격하고 shipping packet을 만든다

PM Skills 2.0의 /red-team-prd는 pre-mortem보다 더 실행 지향적이다. "이미 실패했다고 가정"하는 데서 멈추지 않고, 현재 PRD의 살아있는 claim을 뽑아 Fails if와 Cheapest test로 바꾼다. PM의 역할은 좋은 문장을 쓰는 것이 아니라 가장 싼 검증으로 틀린 가정을 빨리 죽이는 쪽으로 이동한다.

AI Shipping Kit의 /ship-check도 같은 변화다. AI가 만든 코드를 사람이 서명 가능한 상태로 만들려면 아키텍처, 권한, 환경변수, 테스트, 보안·성능 감사가 하나의 packet으로 묶여야 한다. 핵심 관문은 **intended vs. implemented** — 문서화된 의도와 실제 구현 사이의 간극을 PM이 검토 가능한 형식으로 만드는 것이다.

## 관련 개념

- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
- [pm-agency-ai-era](/concepts/pm-agency-ai-era.md)
- [team-decision-structure-agent-era](/concepts/team-decision-structure-agent-era.md)
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [claude-code](/tools/claude-code.md)
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- [agent-pricing-model](/concepts/agent-pricing-model.md)
- [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)
- [claude-code-vs-codex-economics](/insights/claude-code-vs-codex-economics.md)
- 260515_openclaw
- [karpathy](/people/karpathy.md)
- anthropic
- openai
- [geoffrey-hinton](/people/geoffrey-hinton.md)
- [yann-lecun](/people/yann-lecun.md)
- [demis-hassabis](/people/demis-hassabis.md)
- [ai-education-evolution](/concepts/ai-education-evolution.md)
- [llm-deployment-patterns](/concepts/llm-deployment-patterns.md)
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)
- [agent-skill-optimization](/insights/agent-skill-optimization.md)
