---
type: tool
title: Gemini Spark
description: Google이 I/O 2026 (2026-05-19) 에서 발표한 24/7 동작하는 개인 agentic assistant.
tags:
- gemini
- agentic-ai
- mcp
- multi-agent
timestamp: '2026-05-22'
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Gemini Spark

Google이 **I/O 2026 (2026-05-19)** 에서 발표한 24/7 동작하는 개인 agentic assistant. Gemini base 모델 + **Google Antigravity agentic harness** 위에 구축됐다. Google AI Ultra 구독자에게 다음 주(2026-05-26 주) 공개 예정.

## 핵심 차별점

- **Gmail/Workspace out-of-the-box 통합** — 사용자가 별도 권한·OAuth 설정 없이 Gmail, Docs, Sheets, Slides를 바로 활용. Google이 가진 구조적 advantage(이미 모든 이메일을 보유)을 살린 포지셔닝
- **Cloud VM 상주 실행** — 사용자 laptop 열어둘 필요 없이 dedicated VM에서 long-horizon task 수행
- **Email 인터페이스** — 전용 Gmail address로 Spark에 작업 지시 가능
- **Web 직접 조작** — Chrome 통합으로 페이지 탐색·입력
- **모바일 진행 추적** — Android Halo 시스템으로 진행 상황 모니터링
- **MCP 확장** — 외부 서비스도 MCP 통해 연결, 향후 connector 확대 예정

## 포지셔닝 — 비교군

같은 24/7 agentic personal assistant 카테고리에서 직접 비교군:

| 제품 | 회사 | 차별 자산 |
|------|------|----------|
| **Gemini Spark** | Google | Gmail + Workspace + Chrome 통합 |
| Claude Cowork | Anthropic | 코드/문서 agentic workflow ([claude-code](/tools/claude-code.md) 라인) |
| ChatGPT agent | OpenAI | broad-purpose web agent ([openai-agents-sdk](/tools/openai-agents-sdk.md) 라인) |

## 활용 시나리오 (인용)

> "Need to send an email to your boss with a status update? Spark can pull all the facts from your emails, your docs, your sheets, and slides and write the draft for you."
> — Josh Woodward, VP Gemini App and AI Studio

> "Small businesses are using Spark. They can watch over their inbox, so they never miss a question from a customer."

## 의미 — 시장 함의

- 개인 agentic assistant 경쟁이 **base model 우열**에서 **데이터·workflow 접근권**으로 이동
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) 관점: 사용자 한 명이 동시에 굴릴 수 있는 에이전트 수 N이 OS 레벨(Android Halo)·이메일 계정 레벨로 확장
- [agent-harness-pattern](/concepts/agent-harness-pattern.md) 관점: harness(Antigravity) + base model 분리 패턴이 빅테크 표준이 되어 가고 있음
- [agent-pricing-model](/concepts/agent-pricing-model.md) 관점: Ultra 구독 묶음으로 outcome 단위가 아닌 **suite 단위** 과금. [vertical-depth](/concepts/vertical-agent-domain-depth.md)도 아닌 horizontal 묶음 전략
- [ai-pm-role](/concepts/ai-pm-role.md) 관점: workplace agent가 IT 부서 통제를 우회하고 직접 worker에게 도달 → governance 압박 증가

## 관련 페이지

- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) — 24/7 동작·N 동시성 KPI
- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — Generator-Evaluator + harness 구조
- google-antigravity — Spark의 기반 harness
- [claude-code](/tools/claude-code.md) — Anthropic 비교군
- [openai-agents-sdk](/tools/openai-agents-sdk.md) — OpenAI 비교군
- [agent-pricing-model](/concepts/agent-pricing-model.md) — Ultra 구독 묶음 과금
- [ai-governance-verification](/concepts/ai-governance-verification.md) — Workspace 통합형 agent의 governance 표면

## 출처

- TechCrunch, "Google introduces Gemini Spark, a 24/7 agentic assistant with Gmail integration, at IO 2026" (2026-05-19) — Russell Brandom
