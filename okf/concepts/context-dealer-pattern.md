---
type: concept
title: Context Dealer 패턴
description: PM은 문서 작성자가 아니라 AI에게 맥락(context)을 나눠주는 사람(dealer) 이다.
tags:
- context-dealer
- pm-paradigm
- agent-design
timestamp: '2026-05-29'
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

# Context Dealer 패턴

## 한 줄 정의

> PM은 문서 작성자가 아니라 **AI에게 맥락(context)을 나눠주는 사람(dealer)** 이다.

카드 게임의 딜러처럼, PM은 각 AI 에이전트에게 "지금 이 판에서 필요한 패"를 정확히 나눠준다. 패가 좋아야 에이전트가 좋은 수를 둔다.

---

## 왜 이 패턴이 필요한가?

**기존 PM의 역할**: 기획서 쓰기 → 개발자에게 전달 → 리뷰 → 수정  
**AI 시대 PM의 역할**: 문제 정의 → AI에게 맥락 전달 → 결과 검증 → 이터레이션

AI는 실행력이 뛰어나지만 **배경 지식이 없으면 엉뚱한 방향으로 달린다**.  
"이 서비스의 타깃은 40대 자영업자야", "법적 제약 때문에 이 표현은 못 써" 같은 맥락이 없으면 좋은 결과물이 나오지 않는다.

[instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)는 이 문제를 모델 학습 단계에서 풀었다 — 인간 피드백으로 모델이 원하는 컨텍스트를 내면화하도록. Context Dealer 패턴은 그 철학을 런타임 레이어에서 매 요청마다 실천하는 것이다. [ai-education-evolution](/concepts/ai-education-evolution.md)이 보여주듯, AI 리터러시가 높은 PM일수록 이 맥락 주입을 더 정밀하게 설계한다.

---

## 핵심 공식

```
문제 정의 (시작)  +  평가 기준 (끝)  =  모델이 중간을 채운다
```

- **문제 정의**: "무엇이 해결되면 성공인가?" — AI가 무엇을 향해 달릴지 알게 됨
- **평가 기준**: "어떻게 확인할 수 있는가?" — AI가 스스로 검증할 수 있게 됨
- **모델**: 중간 경로(how)는 AI가 알아서 최적화함

### 나쁜 예 vs 좋은 예

| 나쁜 프롬프트 | 좋은 프롬프트 |
|---|---|
| "마케팅 이메일 써줘" | "40대 자영업자 대상, 법률 AI 서비스 런칭 이메일. 두려움보다 효율을 강조. 100자 이내 제목 포함." |
| "코드 리뷰 해줘" | "Python FastAPI, 주니어 개발자 코드. 보안 취약점 우선, 스타일은 나중에. 수정 제안은 코드로." |

---

## 실천 4단계

1. **문제 정의** — "무엇이 해결되면 성공인가?" 한 문장으로
2. **컨텍스트 주입** — 도메인 지식 + 제약 + 히스토리를 AI에 전달
3. **평가 기준 설정** — 결과를 검증할 수 있는 기준 명시 (Eval First)
4. **결과 검증** — 기준 대비 결과 확인 → 맥락 보정 → 재실행

> 실패의 80%는 맥락 부족이지, AI의 능력 부족이 아니다.

### 2026-05-28 블로그 압축

2026-05-28 Context Dealer 블로그는 이 패턴을 제품 철학 문장으로 재정리했다: **문제 정의(시작) + 평가 기준(끝) = 모델이 중간을 채운다.** PM이 붙잡아야 할 것은 How가 아니라 What과 Criteria다. “마케팅 이메일 써줘”가 아니라 타깃, 도메인, 톤, 길이, 성공 기준을 함께 주는 것이 좋은 패다.

이 글의 중요한 보강은 Spec보다 Eval을 먼저 둔다는 점이다. “이 작업이 끝났을 때 어떤 상태면 성공인가?”에 답하지 못하면 아직 에이전트나 기능 명세를 쓸 단계가 아니다. 이해는 AI에게 위임할 수 없고, 결과가 우리 상황에서 의미하는 바를 PM이 직접 한 문단으로 남겨야 한다.

---

## Multi-Agent에서의 적용

에이전트가 여러 개일 때 Context Dealer는 더 중요해진다.  
각 에이전트는 **자신이 받은 컨텍스트만큼만** 잘한다.

```
사용자 의도
    ↓
Orchestrator (MT-00) — 의도 파악 + 태스크 분배
    ↓
Context Dealer (MT-03) — Notion/Memory에서 도메인 맥락 추출 + 주입
    ↓
실행 에이전트들 — 각자 맡은 도메인에서 맥락 기반 실행
```

- **잘못된 방식**: 모든 에이전트에게 전체 컨텍스트 전달 → 노이즈 증가, 비용 낭김
- **올바른 방식**: 에이전트별로 필요한 조각만 선택적으로 주입 ([tiago-forte](/people/tiago-forte.md)의 PARA 방법론에서 distill을 위임하는 정신과 맥락이 닿는다)

[geoffrey-hinton](/people/geoffrey-hinton.md)이 역전파(backpropagation)로 "오차 신호를 레이어별로 정확히 전달"하는 구조를 설계한 것처럼, Context Dealer도 신호(맥락)를 에이전트별로 정밀하게 라우팅한다. [yann-lecun](/people/yann-lecun.md)의 로컬 예측 모델 비판도 같은 맥락 — 전체 컨텍스트를 한 번에 넘기는 것이 아니라 계층적으로 필요한 정보만 흘리는 것이 핵심이다.

---

## 연결 개념
- 260515_100_agents — 100-agent 팀에서의 실제 구현
- habix-profile — 비즈니스 컨텍스트 소스
- agent-memory-pattern — 맥락을 저장·불러오는 메모리 패턴
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 오케스트레이션 설계 원칙
- [tiago-forte](/people/tiago-forte.md)
- [karpathy](/people/karpathy.md)
- [ai-education-evolution](/concepts/ai-education-evolution.md)
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)
- [geoffrey-hinton](/people/geoffrey-hinton.md)
- [yann-lecun](/people/yann-lecun.md)
