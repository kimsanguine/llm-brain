---
type: insight
title: Claude Code vs Codex CLI — 경제성·실패 모드·MCP 브릿지
description: 가장 많이 출하하는 엔지니어는 둘을 비교해서 하나 고르지 않는다.
tags:
- claude-code
- mcp
- workflow-pattern
- cost-optimization
timestamp: '2026-05-25'
x-llmbrain-domain:
- tools
- AI/LLM
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Claude Code vs Codex CLI — 경제성·실패 모드·MCP 브릿지

## 핵심 원칙

가장 많이 출하하는 엔지니어는 둘을 비교해서 하나 고르지 않는다. **둘을 묶어 한쪽이 다른 쪽을 자동 리뷰하게 wire**한다. 비교 프레임이 함정. 두 도구는 서로 반대 방식으로 실패한다.

원칙: **틀린 코드 비용이 가장 큰 곳에는 Claude Code, 빠른 검증이 가능한 곳에는 Codex CLI.**

## 발견된 패턴

### 비용 격차 (Express.js 백엔드 리팩터 실측, DiamantAI 2026-05-21)
- Claude Code: ~$155
- Codex CLI: ~$15
- 광고된 "4×"가 아니라 **10×** 차이
- 핵심 원인: Claude Code의 narrate-before-act 출력 토큰 + Opus 4.7이 GPT-5.4 대비 출력 단가 5×

### 구독 함정
- Claude Code Pro $20 → 복잡 프롬프트 5개로 한도 소진 → Max $100/$200 이주 압박
- OpenAI는 2026-04 조용히 agentic Codex 워크플로우를 flat subscription에서 API metering으로 이관. "포함됐다고 생각한" 세션이 수천 달러 청구 사례 다수
- 결국 선택은 "어떤 빌링 서프라이즈를 감내할 것인가"

### Claude Code 시그니처 실패 — Context Drift
- 3시간 연속 세션 후 codebase 대신 1시간 전 본인 발언을 참조 시작
- 멀티파일 리팩터에서 가장 심각: 주 파일 깔끔 수정 → 의존 체인 상실 → import/export 수동 stitching 1시간
- **테스트 생성 silent 버그**: green check 통과하지만 잘못된 동작 검증. 브라우저 API를 preemptive mock해 검증해야 할 로직을 silent bypass. (CLAUDE.md Rule 6 "Tests verify intent" 위반의 자동화판)

### Codex CLI 시그니처 실패 — "Almost-Correct" 코드
- 컴파일 OK, 기존 테스트 통과, 프로덕션 부하에서만 터지는 통합 버그
- /goal 세션이 25시간 무인 가동, 토큰 1300만, 코드 3만 라인 — 아무도 안 읽음 → 미묘한 disaster 머지
- CI에서 silent hang: codex-yolo alias 또는 approval policy override 없으면 approval prompt에서 무기한 runtime 소진

### MCP Bridge — 표준 패턴
공식 플러그인 **openai/codex-plugin-cc** 한 번 설치로 Codex CLI를 Claude Code 내부 MCP 서버로 wire.

워크플로우:
1. Claude Opus Plan agent → codebase 리서치 + 구조화된 계획
2. Codex가 계획을 정확성·보안 측면에서 audit (코드 한 줄 작성 전에)
3. Claude Sonnet이 합의된 계획 구현 (비용 절감)
4. Codex가 git diff 리뷰 → APPROVED / WARNING / BLOCKED 3중 verdict
5. BLOCKED → 최대 3회 자동 repair 사이클, 사람 개입 없음

**왜 중요한가**: AI 에이전트는 자기 일을 리뷰 못 함. 특히 Claude는 자기 출력에 stubborn + sycophantic. 다른 모델 패밀리로 리뷰 라우팅하는 것이 mechanical solution. [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)의 도구 레벨 실현체.

### 가벼운 setup
플러그인 없이도 2 터미널 탭 + 공유 instruction 파일.
- Codex CLI: AGENTS.md 네이티브 읽음
- Claude Code: CLAUDE.md에 `@AGENTS.md` import 라인 한 줄. 5초 설정, 6개월 드리프트 방지

## 적용 방법

### 단일 도구 선택 가이드 (DiamantAI 디폴트 매트릭스)

| 작업 | 기본값 | 이유 |
|------|-------|------|
| Frontend 작업 | Claude Code | 블라인드 리뷰어 선호도 약 2/3 |
| 멀티파일 리팩터 (감독 가능 시) | Claude Code | 구조 무결성 |
| 복잡 기능, React | Claude Code | 품질 격차 (SWE-bench 점수 근접해도) |
| 자율 배치 작업 | Codex CLI | Terminal-Bench 2.0 12점 우위 |
| DevOps 스크립트, scaffolding | Codex CLI | 빠른 테스트로 검증 |
| 셸 기반 작업 | Codex CLI | 시스템 관리 신뢰성 |
| 규제 코드 | Codex CLI | Seatbelt/Landlock/bwrap 커널 sandbox, 네트워크 default off |

### 안티 패턴
- "열려있는 도구"로 다음 태스크 처리 → premium Claude 토큰으로 boilerplate scaffold, Codex CLI가 빌링 로직 silent 재작성

### 둘 다 못 막는 것
- 잘못된 instruction: AGENTS.md에 "모든 네트워크 call retry" → 한 endpoint가 retry 금물이어도 둘 다 버그 출하
- 약한 테스트 suite: Claude는 잘못된 assert하는 passing test로 더 악화, Codex 야간 run의 stopping test가 신뢰 가능해야 가치 발생

## 한국 시장 맥락 (Newneek 2026-05-22)
한국 사무직 사이에서도 "AI 모델 경쟁력 = 단순 응답력 → 실제 업무 효율"로 기준 전환. ChatGPT vs Claude 라이벌 구도 인식이 일반 직장인 레이어까지 확산. habix-profile 컨설팅 제품의 청중 reach가 expanding.

## 2026-05-25 보강: 멀티 AI PM 워크플로우

Codex와 Claude를 동시에 쓰는 PM 워크플로우는 “어떤 도구가 더 좋은가” 논쟁에서 벗어난다. 기준은 **자율성 × 사용 환경**이다. 터미널에서 빠르게 실행하고 검증할 작업은 Codex가 강하고, 긴 맥락의 제품 판단·리뷰·문서화는 Claude 계열이 강하다.

표준 패턴은 다음과 같다.

1. PM이 목표와 평가 기준을 명시한다.
2. 한 모델이 구현 또는 초안을 만든다.
3. 다른 모델이 비용·보안·정확성 관점에서 리뷰한다.
4. 사람은 최종 승인과 제품 판단에 집중한다.

이 흐름은 [ai-pm-role](/concepts/ai-pm-role.md)의 “PM은 AI 팀을 운영한다”는 명제를 실제 작업 표면으로 옮긴 것이다.

## 관련 개념
- [openai-codex](/tools/openai-codex.md) — Codex 제품 전체 기능·use case 카탈로그 (이 페이지의 대상 도구)
- [claude-code](/tools/claude-code.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md)
- [model-routing-cost](/concepts/model-routing-cost.md)
- claude-code-workflow
- til-patterns-2026-05
- [agent-build-harness](/insights/agent-build-harness.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
