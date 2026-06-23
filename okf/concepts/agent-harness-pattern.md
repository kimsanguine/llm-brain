---
type: concept
title: 에이전트 하네스 패턴
description: 에이전트 하네스는 LLM을 감싸 확률론적 추론을 결정론적 행동으로 변환하는 런타임 인프라다.
tags:
- agent
- harness
- generator-evaluator
- agent-evaluation
- MCP
timestamp: '2026-06-23'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 3
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 에이전트 하네스 패턴

## 핵심 요약

에이전트 하네스는 LLM을 감싸 확률론적 추론을 결정론적 행동으로 변환하는 런타임 인프라다. OpenAI 4 Pillars와 Anthropic 5 Principles로 대표되며, Generator-Evaluator 분리가 핵심이다. 구현 패턴은 [agent-build-harness](/insights/agent-build-harness.md) 참조.

## 5가지 핵심 구성 요소

arXiv 70개 프로젝트 분석에서 반복 등장한 설계 차원:

| 구성 요소 | 역할 | 대표 구현 |
|---|---|---|
| **Context management** | 모델 컨텍스트 윈도우 제어 | KV-cache, RAG, 압축 |
| **Tool selection** | 에이전트 가능 행동 범위 제한 | 허용 목록, 레지스트리 |
| **Error recovery** | 실패·재시도 로직 | 구조화된 오류 메시지 |
| **State management** | 세션 간 진행 유지 | 파일시스템, git 히스토리 |
| **External memory** | 컨텍스트 밖 정보 저장 | 벡터 DB, JSON 파일 |

## OpenAI 하네스 4 Pillars

1. **Context Architecture** — 에이전트가 보는 컨텍스트 설계 (계층적·점진적 공개)
2. **Agent Specialization** — 역할별 에이전트 분리 (범위 제한 프롬프트 + 제한된 툴)
3. **Persistent Memory** — 세션을 넘는 기억 유지 (대화 히스토리가 아닌 파일시스템 기반)
4. **Structured Execution** — 실행 흐름을 단계로 강제 (Research → Plan → Execute → Verify)

핵심 원칙: **"기계적 강제"** — 유도가 아닌 강제. 코딩 표준을 프롬프트로 요청 → 확률론적. linter가 차단 → 결정론적. [karpathy](/people/karpathy.md)의 nanoGPT가 보여준 "최소한의 구성 요소로 재현 가능한 레퍼런스 구현" 정신이 여기서도 유효하다. [geoffrey-hinton](/people/geoffrey-hinton.md)이 역전파로 확립한 "오차를 레이어별로 역방향 전파"하는 구조는 하네스의 Feedback Loop 계층과 정신적으로 동형이다 — 결과의 오차를 시스템 구조로 역방향 교정한다는 점에서.

## Anthropic 하네스 5 Principles

1. **Constrain** — 에이전트 행동 범위 제한
2. **Inform** — 올바른 맥락과 지침 주입
3. **Verify** — 출력 결과 검증
4. **Correct** — 오류 수정 루프
5. **Human-in-Loop** — 중요 결정 시 인간 개입

핵심 인사이트: **"에이전트는 자기 결과를 정확히 평가하지 못한다"** → Generator-Evaluator 분리 필수. [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)의 RLHF가 바로 이 원칙을 모델 훈련 단계에서 구현한 것 — 하네스는 그 정신을 런타임 인프라로 옮긴다. [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md) LoRA 방식은 에이전트별 파인튜닝 비용을 낮춰 Harness 내부 특화 모델 도입 문턱을 낮추는 실용적 옵션이다.

## 평가 게이트 설계

2026-05-18 PM eval 글에서 정리된 운영 원칙: LLM-as-judge는 유용하지만 P0 업무의 최종 승인자가 되어서는 안 된다. Salesforce식 P0/P1/P2 분류를 팀 업무에 맞춰 적용하고, 위험도가 높은 작업은 자동 점수와 사람 리뷰를 함께 요구한다.

```markdown
P0 (결제·인증·데이터 삭제): 에이전트 95점 + 사람 리뷰 필수
P1 (콘텐츠 생성·분석): 에이전트 90점 자동 통과
P2 (내부 보조 작업): 에이전트 85점 자동 통과
```

핵심은 자동 평가를 없애는 것이 아니라 **어떤 작업에서 자동 평가만으로 충분한지**를 명시하는 것이다. 이 경계가 없으면 데모 품질과 실제 업무 통과율이 분리된다.

## 3계층 구현 구조 (실무)

Augment Code가 정리한 실용 모델:

```
[Constraint Harnesses] — 예방적 제어
  rules 파일, linter, 타입 시스템 → 솔루션 공간 사전 축소

[Feedback Loops] — 수정적 제어
  구조화된 오류 메시지 → 에이전트 자기 수정 가능

[Quality Gates] — 강제 메커니즘
  비준수 코드 머지 차단 → PR 병합 전 검증
```

## arXiv 70개 프로젝트 분포

| 패턴 | 비율 |
|---|---|
| Balanced CLI Framework | 26% |
| Multi-Agent Orchestrator | 31% |
| Lightweight Tool | 21% |
| Scenario-Verticalized | 11% |
| Enterprise Full-Featured | 10% |

가장 중요한 비상관: 프로그래밍 언어 ≠ 아키텍처 패턴. 사용 사례가 결정.

## 신흥 표준 프로토콜

- **MCP (Model Context Protocol)**: 에이전트-툴 수직 상호작용 표준 ("USB-C for AI")
- **A2A (Agent-to-Agent Protocol)**: 이기종 시스템 간 횡적 에이전트 위임

AGENTS.md: 2025년 8월 OpenAI·Google·Cursor·Factory 등이 공동으로 발표한 규칙 파일 표준. 세션 간 지속, 디렉토리 전체 계층적 적용.

## 2026-05-31 보강: 하네스 과잉과 인터페이스 수정

NLP Newsletter의 2026-05-31 논문 묶음은 하네스 설계의 다음 경고를 추가한다. Life-Harness는 agent failure의 큰 비중이 모델 추론 부족이 아니라 model-environment interface mismatch에서 나온다고 본다. action realization, environment contract, trajectory regulation, procedural skill을 runtime fix로 보강하면 모델을 바꾸지 않고도 실패율을 낮출 수 있다.

반대로 Harnesses Are Not Uniformly Better는 하네스가 정교해질수록 항상 좋아지는 것은 아니라고 경고한다. 과도한 분해, 과한 pruning, 실행하지 않은 절차를 실행한 것처럼 믿는 hallucinated execution이 생길 수 있다. 실무 원칙은 모든 단계를 고정하는 것이 아니라, 위험한 전환점과 검증 가능한 계약만 고정하고 나머지는 모델 재량을 남기는 것이다. 이 균형은 agent-evaluation-frameworks와 [agent-build-harness](/insights/agent-build-harness.md)의 회귀 평가로 확인해야 한다.

## 2026-06-22 보강: 루프, 온보딩, Agentic RL

2026-06-22 raw 묶음은 하네스가 단순 wrapper가 아니라 **반복 실행과 조직 온보딩의 운영 레이어**가 되고 있음을 보여준다. Lenny/Huryn의 agent loop 글은 루프를 "조건이 충족될 때까지 자신을 다시 실행하는 프롬프트"로 정의하고, Goal loop를 가장 강한 primitive로 본다. 성공 기준, 최대 pass, 되돌릴 수 없는 작업의 가드레일이 없으면 루프는 생산성 도구가 아니라 토큰 소각기가 된다.

Cloaked의 AI Brain 사례는 새 에이전트 세션을 신입사원 온보딩처럼 취급한다. 역할, 사용 도구, 산출물 형식, 실패 시 연락 경로를 문서와 스크립트로 명시하고, worktree와 Claude Code hook으로 세션을 격리한다. 야간 librarian 에이전트가 기밀 유출을 감시하는 구조는 하네스의 Verify/Correct/HITL 원칙이 회사 운영으로 확장된 사례다.

Agentic RL 프레임워크 신호는 다음 병목을 드러낸다. 일반 RL은 단일 상태-행동-보상 문제에 가깝지만, 에이전트 RL은 긴 시간 지평의 멀티턴 trajectory, 종료 조건, 병렬 rollout 인프라, credit assignment를 함께 다뤄야 한다. 따라서 프로덕션 하네스는 rollout log, step-level reward, final outcome, policy violation을 기록할 수 있어야 한다.

## 프로덕션 수치

- 엔터프라이즈 AI 프로덕션 실패율: 최대 **88%** (하네스 결함 원인: 65%)
- APEX-Agents: 프론티어 모델 전문 작업 첫 시도 통과율 **~24%** (추론이 아닌 오케스트레이션 실패)
- Vercel 툴 간소화: 15개→2개 툴 → 정확도 80%→100%, 토큰 37% 절감, 속도 3.5배
- 하네스 최적화: $3.00→$0.30/MTok (10배 비용 절감)
- Agent loop 실패 조건: 모호한 성공 기준, 최대 pass 부재, 비가역 행동 가드레일 부재
- Agentic RL 병목: 긴 trajectory의 credit assignment, 병렬 환경 rollout, 종료 조건 판정

## 관련 개념

- [agent-build-harness](/insights/agent-build-harness.md) — 실제 구현 패턴 (Constitution 3파일, eval.sh, RALPH Loop)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) — PGE 3-에이전트 패턴 상세
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — 프롬프트→컨텍스트→하네스 3세대 진화
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md) — 에이전트 수 결정 프레임워크
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — Claude Code 기반 실제 하네스 구현
- [context-dealer-pattern](/concepts/context-dealer-pattern.md) — 하네스 내 컨텍스트 공급 역할
- [ai-pm-role](/concepts/ai-pm-role.md) — 평가 기준을 설계하는 PM 역할
- [openai-agents-sdk](/tools/openai-agents-sdk.md) — 실행환경·컴퓨팅 분리의 공식 SDK 구현 (v0.14+, SandboxAgent)
- [karpathy](/people/karpathy.md)
- [swe-agent-aci](/tools/swe-agent-aci.md)
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md)
- [geoffrey-hinton](/people/geoffrey-hinton.md)
- claude-code-workflow
- [agent-skill-optimization](/insights/agent-skill-optimization.md)
