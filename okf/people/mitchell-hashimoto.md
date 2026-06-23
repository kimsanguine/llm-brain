---
type: person
title: Mitchell Hashimoto
description: HashiCorp 공동 창립자 (2012).
tags:
- mitchell-hashimoto
- founder
- hashicorp
- ghostty
- developer-tools
timestamp: '2026-05-26'
x-llmbrain-domain:
- tools
- AI/LLM
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://mitchellh.com
- https://twitter.com/mitchellh
- https://github.com/mitchellh
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Mitchell Hashimoto

## 핵심 요약

HashiCorp 공동 창립자 (2012). Vagrant, Packer, Terraform, Vault 등 인프라 자동화 도구의 원조 저자. 2023년 HashiCorp 사임 후 독립 — **Ghostty** terminal emulator 개발 및 글쓰기·AI 에이전트 연구에 집중하고 있다. 본 wiki에서의 핵심 인용: [harness-engineering-evolution](/concepts/harness-engineering-evolution.md)의 출처 원칙인 **"실수가 구조적으로 재발 불가하게 시스템을 변경한다"** (Hashimoto 원칙).

## 경력

- **2012** — HashiCorp 공동 창립. Vagrant(2010 초기 릴리즈) 원저자로 이미 커뮤니티에서 알려진 상태였음.
- **HashiCorp 시대 (2012–2023)** — Vagrant, Packer, Terraform, Vault, Consul, Nomad 등 오픈소스 인프라 도구군 설계·개발. 각 도구는 minimal interface + composability 원칙을 공유.
- **2023 사임** — HashiCorp CEO 직에서 물러나 독립 개발자로 전환. 이후 HashiCorp는 IBM에 인수(2024).
- **Ghostty** — 독립 후 집중 개발한 GPU-accelerated terminal emulator. Zig 기반, macOS/Linux 크로스플랫폼. 2024년 공개 릴리즈.
- **AI agent harness 연구** — 2024–2025, AI 에이전트 시스템에 인프라 도구 설계 원칙을 적용하는 글쓰기·연구 진행 중.

## 설계 철학

### 1. Hashimoto 원칙 — 시스템 변경으로 재발 방지
단순 버그 수정이 아니라 **"같은 종류의 실수가 구조적으로 재발 불가하도록 시스템 자체를 변경"**. 이는 [harness-engineering-evolution](/concepts/harness-engineering-evolution.md)의 핵심 원칙으로 인용되며, AI 에이전트 harness 설계에서 동일하게 적용된다.

### 2. Minimal interfaces + Composability
Terraform의 provider 모델, Vagrant의 Vagrantfile 패턴 — 모두 "작은 인터페이스, 조합 가능, 재현 가능"이라는 같은 축. LLM 에이전트 시스템의 declarative harness 설계와 직접 연결된다.

### 3. Developer experience 우선
도구가 복잡해도 사용자 접점은 단순하게. Ghostty가 고성능을 유지하면서도 config가 human-readable한 것이 같은 철학의 연장.

## AI/LLM 에이전트 연결

Vagrant·Terraform이 인프라를 **선언적(declarative) + 재현 가능(reproducible) + 조합 가능(composable)**하게 만든 것처럼, 2024–2025 AI agent harness도 같은 원칙으로 설계된다:

- Declarative — 에이전트 행동을 코드로 명시, 런타임 추론에 의존하지 않음
- Reproducible — 같은 입력이면 같은 구조적 결과
- Composable — 각 에이전트/도구가 독립적으로 조합 가능

이 원칙들이 [agent-harness-pattern](/concepts/agent-harness-pattern.md)과 [agent-build-harness](/insights/agent-build-harness.md)의 정신적 선조.

## 관련 개념

- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — Hashimoto 원칙의 1차 인용 페이지
- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — 인프라 도구 철학이 에이전트 시스템에 적용된 패턴
- [agent-build-harness](/insights/agent-build-harness.md) — Hashimoto composability 원칙의 구체적 구현
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — declarative + reproducible harness의 실제 사례
