---
type: concept
title: Recursive Self-Improvement (AI가 AI를 만든다)
description: AI가 자기 자신의 개발을 가속하는 단계.
tags:
- recursive-self-improvement
- ai-safety
- agent-autonomy
- task-horizon
- synthesis-hub
timestamp: '2026-06-07'
x-llmbrain-domain:
- AI/LLM
x-llmbrain-created: '2026-06-07'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Recursive Self-Improvement (AI가 AI를 만든다)

## 핵심 요약

AI가 자기 자신의 개발을 가속하는 단계. 2026-06 Anthropic 내부 진척 리포트(raw 원문 기준)는 이를 예측이 아니라 **측정·문서화된 진행 보고**로 제시한다: 프로덕션 코드베이스에 머지되는 코드의 80%+를 Claude가 작성하고, AI가 사람 개입 없이 자율적으로 일할 수 있는 시간(task horizon)이 해마다 급격히 늘고 있다는 것이다.

## 작동 원리 — 복리(compounding) 개선

핵심 메커니즘은 단순하다. 각 모델이 조금씩 나아지고, 그 다음 모델이 더 빠르게 나아진다. 개선이 다음 개선의 도구가 되므로 곡선이 평탄해지지 않는다.

**Task horizon 지표** (raw 원문 기준 — 신뢰 가능 자율 작업 시간):
- 2024-03: ~4분
- +1년: ~90분
- +1년: ~12시간
- 곡선 유지 시: 2026년 days 단위, 2027년 weeks 단위 진입 전망
- METR이 Claude Mythos Preview에서 16시간+ 자율 작업 측정 — 측정용 벤치마크 길이가 모자라는 상황

**구체 사례 (raw 원문 기준)**:
- 2026-04 Claude가 한 달에 800+ fix를 머지해 한 부류의 API 에러를 1,000배 줄임 — 엔지니어 추정 인간 환산 4년치
- 병목은 지능이 아니라 **한 번에 쥘 수 있는 unfamiliar context의 양**
- self-modifying harness: 에이전트가 자기 scaffolding 코드를 재작성해 SWE-bench +19점 (NLP News)

## Anthropic이 제시한 3가지 미래 (raw 원문 기준)

1. 추세가 정체되어 현재 역량이 경제에 천천히 확산
2. AI 개발이 상당 부분 자동화되지만 방향은 여전히 인간이 설정 *(Anthropic 예상 시나리오)*
3. AI가 자기 후계자를 만들고 진보 속도는 가용 compute가 전적으로 결정

## 보안·검증 함의

Anthropic Project Glasswing은 Mythos Preview를 사이버보안에 적용해 첫 몇 주 만에 주요 시스템에서 10,000+ high/critical 취약점을 발견했다(raw 원문 기준). 의미는 **발견(discovery) 문제는 대부분 풀렸고, 충분히 빠르게 패치하는 대응(response)이 새 병목**이라는 점이다. 거버넌스 측면의 상세는 [ai-governance-verification](/concepts/ai-governance-verification.md)에서 다룬다.

리포트는 글로벌 frontier 개발 일시 중단(pause)이 바람직할 수 있다고 보면서도, 모두가 동시에 하고 부정을 불가능하게 만드는 검증 메커니즘이 있을 때만 그렇다는 단서를 단다. 동시에 "멈추면 덜 신중한 쪽이 앞서간다"는 군비경쟁 논리도 함께 드러난다.

## habix/강의와의 연결점

Ch06 LLM 한계·거버넌스 토론의 최신 실증 사례다. 하네스 엔지니어링 강의 관점에서는 self-modifying harness가 [agent-harness-pattern](/concepts/agent-harness-pattern.md)·[generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)의 다음 단계이고, "AI가 일을 끝내는 속도 > 인간이 검토하는 속도"라는 병목은 [background-agent-n-kpi](/concepts/background-agent-n-kpi.md)(동시 운용 에이전트 수 N)와 직결된다.

## 관련 개념
- anthropic
- [ai-governance-verification](/concepts/ai-governance-verification.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md)
- [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md)
- [frontier-labs-comparison](/concepts/frontier-labs-comparison.md)
