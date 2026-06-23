---
type: concept
title: Generator-Evaluator 아키텍처 (PGE 패턴)
description: 에이전트는 자기 결과를 정확히 평가하지 못한다.
tags:
- generator-evaluator
- multi-agent
- harness
- agent-evaluation
timestamp: '2026-05-16'
x-llmbrain-domain: AI/LLM
x-llmbrain-created: '2026-05-16'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Generator-Evaluator 아키텍처 (PGE 패턴)

## 핵심 요약

에이전트는 자기 결과를 정확히 평가하지 못한다. 이 구조적 한계를 해결하기 위해 Anthropic이 제시한 Planner-Generator-Evaluator(PGE) 3-에이전트 패턴. GAN(Generative Adversarial Networks)에서 영감 받아 생성과 평가를 독립된 에이전트로 분리하는 것이 핵심이다.

## 작동 원리

### 왜 분리가 필요한가

Anthropic 연구 발견: "자기가 생성한 작업물 평가를 요청받으면 에이전트는 명백히 수준 이하일 때조차도 자신 있게 칭찬하는 경향이 있다."

**Self-Assessment Bias (자기 평가 편향)**: 동일 에이전트가 Generator + Evaluator 역할 겸임 → 자기 오류를 식별하지 못하는 구조적 한계.

이는 단순한 프롬프트 개선으로 해결되지 않는다 — 아키텍처 수준의 분리가 필요하다.

---

### 3-에이전트 구조

```
[사용자 요청]
     ↓
[Planner Agent]
 - 요청 → 상세 스펙으로 확장
 - Sprint 계약 정의 ("완료" 기준 설정)
 - 충분한 컨텍스트를 포함한 청크 분해
     ↓
[Generator Agent]
 - Sprint 계약 기반 코드 구현
 - 단일 컨텍스트 윈도우 내에서 완성
 - 구조화된 출력 전달 (JSON 스펙, 커밋 히스토리, 진행 문서)
     ↓
[Evaluator Agent]
 - 독립적 품질 평가 (미리 정의된 기준)
 - 도구 사용: Playwright로 실제 앱 테스트
 - 타겟 피드백 → Generator로 반환
     ↓ (5-15회 반복)
[최종 결과]
```

---

### 컨텍스트 리셋의 역할

단순 컨텍스트 압축(compaction) vs 완전한 컨텍스트 리셋:
- 압축: 이전 정보의 요약본 유지 → "Context Anxiety" 완전 해소 불가
- **리셋**: 완전히 새로운 컨텍스트로 시작 → 더 깔끔한 성능

PGE 패턴은 각 에이전트가 **독립적 컨텍스트**를 갖도록 설계되어 있어 자연스러운 리셋 효과.

---

## 평가 기준 설계 (Evaluator 구체화)

프론트엔드 작업에서 Anthropic이 사용한 4가지 측정 가능한 기준:

| 기준 | 내용 |
|---|---|
| Design quality | 일관성 및 분위기 |
| Originality | 커스텀 결정 vs 템플릿 |
| Craft | 기술적 실행 품질 |
| Functionality | 사용성과 작업 완료율 |

**원칙**: 주관적 판단을 측정 가능한 기준으로 변환. Evaluator가 "좋다/나쁘다"가 아닌 구체적 점수를 부여해야 Generator가 반복 개선 가능.

---

## 실행 효율성

| 버전 | 하네스 구성 | 시간 | 비용 |
|---|---|---|---|
| Opus 4.5 | Planner + Sprint분해 + Generator + Evaluator | 6시간 | $200 |
| Opus 4.6 | Planner + Generator + Evaluator (Sprint분해 제거) | 3.8시간 | $124.70 |

**통찰**: 모델이 개선되면 하네스 구성 요소를 제거할 수 있다. 하네스의 각 요소는 "모델이 혼자 할 수 없는 것에 대한 가정"이며, 그 가정은 정기적으로 재검토해야 한다.

---

## arXiv 70개 프로젝트 분석 결과

Multi-Agent Orchestrator 패턴(PGE 포함)이 전체의 **31%**로 가장 일반적.
특징: 명시적 조율 + 계층적 메모리 + 정책 보안.

공통 발견: 더 깊은 조율 ↔ 더 정교한 상태 관리가 함께 등장.

---

## 활용 사례

- **Anthropic**: 멀티 시간 풀스택 개발 세션 (게임, DAW 프로토타입)
- **코드 리뷰**: Generator(PR 작성) + Evaluator(독립 리뷰 에이전트)
- **콘텐츠 파이프라인**: Generator(초안) + Evaluator(사실 확인 + 톤 검수)
- **강의 자료 제작**: 병렬 에이전트 분할 편집 + 독립 품질 검수

## habix/강의와의 연결점

**habix**: Agent100 빌드에서 Constitution + eval.sh가 바로 Evaluator 역할. 실패 → 규칙 승격 패턴이 Evaluator의 피드백을 Planner의 다음 Sprint 계약에 반영하는 구조.

**강의**: "에이전트는 자기 결과를 평가 못 한다"는 사실을 학생들에게 보여주기 좋은 사례 — 같은 모델에 "이 코드 좋아?" 물으면 항상 "좋습니다"가 나오는 실험으로 직접 체험 가능.

## 관련 개념

- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — PGE를 포함한 전체 하네스 프레임워크
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — Generator-Evaluator가 3세대에서 핵심 패턴인 이유
- [agent-build-harness](/insights/agent-build-harness.md) — eval.sh + RALPH Loop 실제 구현
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md) — PGE를 쓸 때와 단일 에이전트로 충분할 때
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 컨텍스트 리셋 전략
