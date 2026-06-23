---
type: tool
title: SWE-agent & Agent-Computer Interface (ACI)
description: Princeton 팀(John Yang, Carlos E. Jimenez 등)이 2024-05 발표한 자율 소프트웨어 엔지니어링
  에이전트 시스템.
tags:
- swe-agent
- aci
- agent-computer-interface
- multi-agent
timestamp: '2026-05-22'
x-llmbrain-domain:
- AI/LLM
- tools
- agent
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# SWE-agent & Agent-Computer Interface (ACI)

## 핵심 요약

Princeton 팀(John Yang, Carlos E. Jimenez 등)이 2024-05 발표한 자율 소프트웨어 엔지니어링 에이전트 시스템. 핵심 주장은 **"LM 에이전트는 새로운 카테고리의 end user이며, 인간이 IDE를 쓰듯 specially-built interfaces가 필요하다"** — 이 인터페이스를 **Agent-Computer Interface (ACI)** 로 정의한다. SWE-bench에서 pass@1 12.5%, HumanEvalFix 87.7%로 당시 SOTA 달성.

## 주요 기능

### ACI 설계 원칙
- LM 에이전트가 컴퓨터를 자율적으로 사용하도록 돕는 커스텀 인터페이스 레이어
- 파일 생성·편집, 전체 리포지토리 탐색, 테스트·프로그램 실행 능력 제공
- 인간용 GUI/CLI가 아닌, 에이전트의 인지 특성에 맞춘 별도 추상

### 평가 벤치마크
| 벤치마크 | SWE-agent pass@1 | 의미 |
|---|---|---|
| SWE-bench | 12.5% | 실제 GitHub 이슈 해결 (non-interactive LM 대비 큰 폭 우위) |
| HumanEvalFix | 87.7% | 버그 fix 능력 |

## 사용 패턴

- **공식 배포**: [swe-agent.com](https://swe-agent.com) — 코드·데이터·데모 공개
- **버전 이력**: v1 2024-05-06 → v3 2024-11-11
- **저자 소속**: Princeton (John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press)
- **arXiv 분류**: cs.SE / cs.AI / cs.CL / cs.HC / cs.LG

## 본 wiki의 컨텍스트에서

ACI 개념은 본 wiki의 기존 에이전트 관련 클러스터와 직접 맞물린다:

- **vs [agent-harness-pattern](/concepts/agent-harness-pattern.md)**: 하네스가 "에이전트 외부 시스템(generator-evaluator 분리, P0/P1/P2 평가 게이트)"이라면, ACI는 "에이전트가 컴퓨터·도구와 상호작용하는 인터페이스 레이어". 두 개념은 직교한다.
- **vs [claude-code-agent-system](/tools/claude-code-agent-system.md)**: Claude Code의 `.claude/agents/` 폴더 패턴 + Bash/Read/Edit tool은 사실상 Claude Code 안에 내장된 ACI다. SWE-agent의 ACI는 별도 시스템 외부에 구축한 형태.
- **vs [single-vs-multi-agent](/concepts/single-vs-multi-agent.md)**: SWE-agent는 single-agent 패턴. ACI 디자인이 좋으면 single agent가 SOTA 달성 가능함을 보여준 사례.
- **vs [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)**: SE 도메인 깊이 + ACI를 결합해 버티컬 에이전트 경쟁력 확보 (SWE-bench SOTA가 그 증거).

## 주의사항 / 함정

- **벤치마크 시점 주의**: 본 데이터는 2024-05 v1 기준. 2025-2026 frontier 에이전트(Claude Code, Cursor, Devin 등)는 SWE-bench에서 더 높은 점수 달성 — 절대값보다 ACI 설계 영감이 핵심 가치.
- **"새로운 end user" 주장의 한계**: 에이전트가 정말로 인간과 분리된 user인지 (또는 LLM 호출 wrapper인지)는 철학적 논쟁 영역. 다만 인터페이스 디자인 결정에서 실용적 효과 입증됨.

## 관련 개념
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [agent-build-harness](/insights/agent-build-harness.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md)
- [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)
