---
type: insight
title: 에이전트 스킬 최적화
description: 에이전트의 반복 성능은 프롬프트 한 번이 아니라 스킬 문서라는 자연어 상태를 얼마나 잘 설계하고 갱신하느냐에 달려 있다.
tags:
- agent-skill
- claude-code
- skillopt
- workflow-pattern
timestamp: '2026-06-22'
x-llmbrain-domain:
- AI/LLM
- agent engineering
x-llmbrain-created: '2026-06-01'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 에이전트 스킬 최적화

## 핵심 원칙

에이전트의 반복 성능은 프롬프트 한 번이 아니라 **스킬 문서라는 자연어 상태**를 얼마나 잘 설계하고 갱신하느냐에 달려 있다. SkillOpt는 compact natural-language skill document를 frozen agent의 trainable state로 보고, rollout·reflection·validation-gated edit로 개선한다. Josh Pigford의 `/build`, `/adversarial-code-review`, `/but-for-real`, `/learnings` 운영도 같은 원리의 실무형 구현이다.

## 발견된 패턴

### 2026-05-31 — SkillOpt: 스킬 문서를 학습 가능한 상태로 보기

Microsoft Research의 SkillOpt는 모델 가중치를 바꾸지 않고, 작은 자연어 스킬 문서를 add/delete/replace 방식으로 수정한다. 중요한 점은 모든 수정이 held-out validation gate를 통과해야 유지된다는 것이다. 즉 스킬 작성은 감각적 문서 편집이 아니라 측정 가능한 optimization loop가 된다.

raw newsletter 기준으로 SkillOpt는 Trace2Skill, TextGrad, GEPA, EvoSkill, human-written skills를 6개 benchmark와 7개 target model에서 이겼고, GPT-5.5 direct chat, Codex loop, Claude Code baseline 모두에서 큰 향상을 보였다. 숫자보다 중요한 해석은 병목이 base model capability에서 **agent 주변 자연어 상태를 훈련하는 능력**으로 이동한다는 점이다.

### 2026-05-31 — 솔로 빌더의 스킬 운영

Josh Pigford의 Claude Code 스택은 스킬을 작업 습관으로 분해한다.

- `/build`: Research → Plan → Track → Implement의 4단계 구현 플로우
- `/adversarial-code-review`: 한 모델이 만든 코드를 다른 모델 패밀리에게 리뷰시켜 자기평가 편향을 줄임
- `/but-for-real`: push 전 추가 버그를 강제로 찾는 검증 루틴
- `/learnings`: AI가 자체 CLAUDE.md를 업데이트하게 만들어 반복 품질을 개선

이 구조는 [agent-build-harness](/insights/agent-build-harness.md)의 하네스 원칙과 직접 연결된다. 스킬은 명령어 모음이 아니라 반복 가능한 작업 회로다.

### 2026-05-31 — Workstation vs Skill 구분

CoolDeep의 Cowork 팁은 Skill과 Workstation을 구분한다. 중간에 판단이 필요한 진행형 프로세스는 Workstation, 산출물 형태가 이미 정해진 반복 작업은 Skill이다. 이 구분을 못 하면 모든 작업을 무거운 workspace로 만들거나, 반대로 판단이 필요한 작업을 얇은 스킬에 넣어 품질이 흔들린다.

실무 테스트는 단순하다. "이 작업 중간에 결정을 내려야 하나?" Yes면 Workstation, No면 Skill이다.

### 2026-06-21 — 스킬 양산 금지와 정착률 검증

2026-06-21 TIL의 실제 프롬프트 로그 분석은 스킬 제작의 반대편 지표를 보여준다. 개인 스킬 29개 중 `/wrapup`만 65회 정착했고, 나머지 28개는 0~7회 사용에 머물렀다. 즉 스킬은 "만들 수 있다"가 아니라 "반복 호출될 만큼 분명한 작업 회로인가"로 판단해야 한다.

이날 `/ship`은 보수적 트리거, 배포 직전 echo, `verify_live.sh`, deploy target 명시, harness 등록 확인까지 거쳐 활성화됐다. 반대로 `/poll`은 유용성이 확인됐지만 입력 경로(PID/로그 인자 vs 자동 감지)가 결정되지 않아 제작을 보류했다. 좋은 스킬화 판단은 아이디어를 빨리 파일로 만드는 것이 아니라, 호출 조건·입력 경로·검증 게이트가 분명할 때만 만들고 나머지는 보류하는 것이다.

### 2026-06-22 — 문서 처리와 persistent context로서의 Skill

AI Engineering의 ADE Document Processing Skills 사례는 스킬이 프롬프트 템플릿을 넘어 **도메인 처리 파이프라인**이 될 수 있음을 보여준다. `document-extraction`은 문서를 구조화 Markdown으로 파싱하고 JSON schema/Pydantic 모델로 필드를 추출하며, `document-workflows`는 classify -> extract -> chunk/embed -> export 흐름을 배치로 실행한다. 즉 좋은 스킬은 한 문장 지시가 아니라 입력 유형, 중간 산출물, 검증 가능한 출력 스키마를 가진 작은 제품이다.

CoolDeep의 Claude Skills 글들은 같은 원리를 개인 사용성 관점에서 보강한다. Projects는 영구 컨텍스트 레이어, Skills는 재사용 가능한 업무 절차, MCP Connectors는 외부 도구 접근, Files API + prompt caching은 대용량 컨텍스트 재사용 비용 절감이다. 핵심은 "좋은 답을 한 번 얻기"가 아니라 브랜드 보이스, 검토 기준, 문서 처리 규칙, 루프 종료 조건을 persistent context로 저장하는 것이다.

Lenny의 주간 Skills loop 사례는 스킬 갭 식별 -> 새 skill 작성 -> goal loop 검증 -> 실패 사례 반영의 재귀적 자기개선 구조다. 다만 2026-06-21 TIL의 정착률 데이터와 함께 보면 결론은 보수적이다. 스킬은 만들기보다 **사용 로그와 검증 루프를 통과한 반복 작업만 승격**해야 한다.

## 적용 방법

1. 반복 작업을 먼저 스킬 후보로 분리한다.
2. 스킬 파일에는 목표, 입력 형식, 처리 절차, 실패 시 중단 조건, 검증 방법만 남긴다.
3. 실행 후 실패 사례를 `/learnings`처럼 스킬 문서에 반영하되, 검증 없이 규칙을 늘리지 않는다.
4. 중요한 스킬은 held-out task나 fixture를 만들어 회귀 테스트한다.
5. 새 스킬을 만들기 전 기존 로그에서 반복 빈도와 실패 비용을 확인한다.
6. 비가역 스킬은 명시 호출, 실행 직전 echo, 라이브 검증, 런타임 활성화 관측을 기본 게이트로 둔다.
7. 문서 처리 스킬은 입력 포맷, 추출 schema, 실패 기준, export target을 함께 정의한다.
8. 새 스킬은 사용 빈도와 실패 비용을 본 뒤, goal loop나 held-out task로 검증하고 승격한다.

## 관련 개념

- [agent-build-harness](/insights/agent-build-harness.md)
- agent-evaluation-frameworks
- claude-code-workflow
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
