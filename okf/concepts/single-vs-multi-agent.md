---
type: concept
title: 단일 에이전트 vs 멀티 에이전트 결정 프레임워크
description: 멀티 에이전트가 항상 더 좋지 않다.
tags:
- multi-agent
- orchestration
- agent-evaluation
timestamp: '2026-05-16'
x-llmbrain-domain: AI/LLM
x-llmbrain-created: '2026-05-16'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 단일 에이전트 vs 멀티 에이전트 결정 프레임워크

## 핵심 요약

멀티 에이전트가 항상 더 좋지 않다. 병렬화 가능한 작업에서는 81% 향상을 보이지만 순차 작업에서는 70% 저하가 발생한다. 작업의 병렬화 가능성, 컨텍스트 포화 여부, 읽기/쓰기 구조 세 가지 기준으로 판단해야 한다.

## 작동 원리

### 결정의 3가지 핵심 축

**축 1: 작업 병렬화 가능성**
- Google 연구: 병렬화 가능한 작업 → 멀티 에이전트 **+81%**
- 순차적 작업 → 멀티 에이전트 **-70%**
- 판단 기준: 작업이 독립적 모듈로 분리되는가?

**축 2: 컨텍스트 윈도우 포화**
- 단일 에이전트 컨텍스트 과부하 → 정확도 눈에 띄게 저하
- 단, 실제 포화는 토큰 예상이 아닌 **테스트로 확인** 필요
- 포화 전이라면 단일 에이전트가 오버헤드 없이 유리

**축 3: 읽기/쓰기 구조**
- 읽기 중심 (정보 수집·리서치) → 병렬화 적합
- 쓰기 중심 (코드베이스 수정) → 순차적 조율 필요 (병합 충돌 위험)

---

### 시나리오별 결정표

| 작업 유형 | 권장 | 근거 |
|---|---|---|
| 단일 파일 편집·디버깅 | 단일 에이전트 | 상태 일관성이 병렬성보다 중요 |
| 표준 코드 리뷰 | 단일 에이전트 | 컨텍스트 연속성 필수 |
| 광범위 리서치·정보 수집 | 멀티 에이전트 | Anthropic 데이터 **+90.2%** |
| 독립 모듈 리팩토링 | 멀티 에이전트 (조건부) | 모듈이 독립적 변환 가능할 때만 |
| 전문 분야별 코드 리뷰 | 멀티 에이전트 | 독립 도메인은 병렬 가능 |
| 의존성 있는 기능 개발 | 단일 에이전트 | 의존성 체인이 순차 강제 |

---

## 비용 현실

**UIUC 연구** 기준 멀티 에이전트 토큰 소비:
- 단순 멀티 에이전트: 기준 대비 **4~220배** 토큰
- 최적화된 멀티 에이전트: **2~12배** 응답 생성 토큰

→ 멀티 에이전트를 쓰는 이유가 "복잡해 보여서"라면 비용만 올라감.

---

## 멀티 에이전트의 4가지 구조적 실패 모드

1. **오류 전파**: 상위 에이전트 오류 → 하위 에이전트에 복합 전파 → 나중에 발견되는 버그
2. **컨텍스트 손실**: 핸드오프마다 상태 정보 소실
3. **순차 작업 저하**: 의존성 있는 단계에서 조율 오버헤드가 품질 저하
4. **동조적 수렴**: 멀티 에이전트 리뷰에서 에이전트들이 다수 의견에 추종

---

## arXiv 70개 프로젝트에서 보이는 실제 분포

| 아키텍처 패턴 | 비율 | 특징 |
|---|---|---|
| Lightweight Tool | 21% | 단일 에이전트 중심 |
| Balanced CLI Framework | 26% | 기본 위임 + MCP |
| Multi-Agent Orchestrator | 31% | 명시적 조율·계층 메모리 |
| Scenario-Verticalized | 11% | 도메인 특화 |
| Enterprise Full-Featured | 10% | 재귀 에이전트·거버넌스 |

**통찰**: 전체의 47%(Lightweight + Balanced CLI)가 단일 에이전트 중심. 멀티 에이전트가 기본값이 아님.

---

## Worktree 격리 패턴

멀티 에이전트 실제 구현의 핵심 인프라:
- 각 에이전트에 독립 git worktree 할당
- 동일 코드베이스를 수정하는 에이전트 간 충돌 방지
- 머지는 리뷰 후 명시적으로 처리

(Claude Code에서: CLAUDE.md `isolation: "worktree"` 파라미터로 자동 관리)

---

## 의사결정 체크리스트

```
1. 작업을 독립 모듈로 분리할 수 있나? → Yes → 멀티 에이전트 검토
2. 각 모듈이 서로 다른 파일/레포를 수정하나? → Yes → 멀티 에이전트 안전
3. 단일 에이전트로 컨텍스트가 실제로 포화되나? (테스트로 확인) → No → 단일로 충분
4. 팀이 조율 오버헤드를 감독할 수 있나? → No → 단일 에이전트 유지
```

## habix/강의와의 연결점

**habix**: OpenClaw의 병렬 에이전트 팀(`isolation: "worktree"`)은 독립 모듈 조건을 충족할 때만 사용. 같은 파일을 여러 에이전트가 수정하면 merge conflict 발생 — CLAUDE.md에 명시된 가드레일.

**강의**: 학생들이 "에이전트 많으면 좋다"고 착각하는 경향에 대한 직접적인 교정 사례. 비용 데이터(4~220배)와 Anthropic 리서치(+90.2% vs -70%)를 함께 보여주면 직관적.

## 관련 개념

- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) — 멀티 에이전트의 대표 패턴 (PGE)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — 멀티 에이전트 오케스트레이션 전체 프레임워크
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — 단일/멀티 선택이 하네스 설계의 일부인 이유
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 컨텍스트 포화 전 단일 에이전트 최적화
- [agent-build-harness](/insights/agent-build-harness.md) — 실제 병렬 에이전트 구현 사례 (Claude Code worktree)
