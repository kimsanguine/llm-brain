---
type: person
title: John Yang (Princeton)
description: Princeton CS 박사과정생.
tags:
- john-yang
- swe-agent
- swe-bench
- aci
- research-leader
timestamp: '2026-05-26'
x-llmbrain-domain:
- AI/LLM
- research
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/2405.15793
- https://swe-agent.com
- https://www.princeton.edu/~jcyang
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# John Yang (Princeton)

Princeton CS 박사과정생. Princeton NLP Group 소속, Karthik Narasimhan·Ofir Press 지도.

## SWE-agent (2024-05)

**SWE-agent**의 1저자. 논문 "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" (arXiv 2405.15793)에서 **ACI(Agent-Computer Interface)** 개념을 정식 제시했다.

공동 저자: Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press.

### 핵심 주장

> "LM 에이전트는 새 카테고리의 end user다."

인간이 IDE·GUI를 통해 컴퓨터와 상호작용하듯, LM 에이전트에게도 specially-built interface가 필요하다는 논지. 기존 bash shell·파일시스템을 그대로 노출하는 방식은 에이전트의 특성(짧은 컨텍스트, 반복 오류, 탐색 한계)에 맞지 않는다.

## 벤치마크 성과 (당시 SOTA)

| 벤치마크 | 결과 |
|---|---|
| SWE-bench | 12.5% pass@1 |
| HumanEvalFix | 87.7% |

non-interactive LM 기준선 대비 큰 폭 우위 — ACI 설계가 실제 성능 개선으로 이어짐을 실증.

## 후속 연구 방향

- SWE-bench Pro (더 어려운 실제 이슈 벤치마크)
- Multi-agent software engineering
- Robust ACI design (에러 핸들링·상태 추적 개선)

## wiki 내 위치

본 wiki에서 John Yang은 [swe-agent-aci](/tools/swe-agent-aci.md) 페이지의 1저자, [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md) Stage 3(ACI 패러다임 정착)의 핵심 인물로 위치한다.

## 관련 개념

- [swe-agent-aci](/tools/swe-agent-aci.md)
- [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md)
- [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)
