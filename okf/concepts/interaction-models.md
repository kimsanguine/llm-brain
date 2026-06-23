---
type: concept
title: Interaction Models
description: thinking-machines가 2026-05-11에 발표한 새로운 모델 class.
tags:
- omni-modal
- multimodal
- voice-ai
- realtime
timestamp: '2026-05-22'
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Interaction Models

thinking-machines가 2026-05-11에 발표한 새로운 모델 class. **interactivity를 외부 software harness가 아닌 model architecture의 first-class citizen**으로 다룬다. Research preview 단계로 일반/엔터프라이즈 공개는 안 된 상태.

## 패러다임 — Turn-based에서 Full-duplex로

기존 frontier 모델은 **단일 thread**로 시간을 인식한다: 사용자 입력 완료 대기 → 처리 → 출력 생성 (생성 중에는 perception 정지). 이 한계가 인간을 "AI 인터페이스에 contort"하게 만든다 — 질문을 이메일처럼 다듬고, 생각을 batch하는 행동.

Interaction model은 이를 **multi-stream, micro-turn 설계**로 우회한다:
- **200ms chunk**의 input/output을 동시 처리
- listen·talk·see가 real-time으로 병렬
- 사용자가 말하는 중에 backchannel("I see", "mm-hmm") 가능
- 시각적 단서를 감지하면 interject (예: 사용자가 코드에 버그를 작성, 화면에 친구가 등장)

## 핵심 기술 — Encoder-free early fusion

Whisper 같은 대형 standalone encoder에 의존하지 않는다. 대신:
- **dMel** raw audio signal 직접 입력
- **40×40 image patches** 직접 입력
- 가벼운 embedding layer로 통과
- 모든 컴포넌트를 transformer 안에서 **scratch부터 co-training**

[whisper-ecosystem](/tools/whisper-ecosystem.md) 같은 외부 STT 파이프라인을 native 모델 안으로 흡수한 형태.

## Dual model 아키텍처

실시간 응답성과 깊은 reasoning은 본질적으로 충돌한다. 이를 두 모델로 분리:

1. **Interaction Model** — 사용자와 항상 대화 유지. dialog management, presence, immediate follow-up 담당
2. **Background Model** — 비동기 agent. 지속 reasoning, web browsing, 복잡한 tool call 처리. 결과를 interaction model에 stream해서 대화에 자연스럽게 weave

발표 데모: 사용자에게 자연스러운 reaction time을 주면서 **동시에** bar chart 생성. live translation을 하면서 사용자 피드백 계속 듣는다.

## 벤치마크 — FD-bench V1.5

`TML-Interaction-Small` (276B MoE, 12B active)의 성능:

| Metric | TML-Interaction-Small | GPT-realtime-2.0 (min) | Gemini-3.1-flash-live (min) |
|---|---|---|---|
| Turn-taking latency (s) | **0.40** | 1.18 | 0.57 |
| Interaction Quality (Avg) | **77.8** | 46.8 | 54.3 |
| IFEval (VoiceBench) | 82.1 | 81.7 | 67.6 |
| Harmbench (Refusal %) | 99.0 | 99.5 | 99.0 |

Interaction Quality 점수가 경쟁군의 **거의 2배**다. RepCount-A(영상 내 반복 카운트)·ProactiveVideoQA(시각 evidence 등장 시 답변) 같은 specialized 테스트에서 다른 frontier 모델은 침묵하거나 오답.

## 비교 — 기존 음성 AI와의 위치

| 시스템 | 패러다임 | 약점 |
|---|---|---|
| [openai-realtime-api](/tools/openai-realtime-api.md) (GPT-realtime-2.0) | Turn-based + low latency | 1.18s latency, encoder chain |
| [gemini-spark](/tools/gemini-spark.md) / Gemini-flash-live | Turn-based | 0.57s latency |
| [hyperclova-x-omni](/tools/hyperclova-x-omni.md) 8B Omni | Unified omnimodal but turn-based | omnimodal 통합 우선, full-duplex 아님 |
| TML-Interaction-Small | **Full-duplex native** | 아직 public 미공개 |

[omnimodality](/concepts/omnimodality.md) 논의가 "input/output modality 조합"을 다뤘다면, interaction model은 한 차원 더 위 — **시간 차원의 동시성**까지 모델에 박아 넣는다.

## 엔터프라이즈 활용 시나리오 (인용)

- **제조·연구실 모니터링**: 영상 feed 감시 중 안전 위반·protocol 이탈을 worker 요청 없이 즉시 interject
- **음성 고객 서비스**: 0.4s latency로 인간 대화 속도. customer 짜증을 듣는 동안 backchannel cue로 끊지 않으면서 live translation
- **시간 인식 process**: "온도를 4분마다 확인", "지난번보다 오래 걸리면 알려줘" 같은 native time-aware 명령 (기존 LLM은 internal clock 없음)

## 의미 — 시장 함의

- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) 시각: harness가 **모델 안으로 흡수**되는 흐름. external orchestrator → native architecture
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) 시각: Voice-to-voice 패턴의 latency·동시성 limit가 native 통합으로 갱신
- [ai-pm-role](/concepts/ai-pm-role.md) 시각: scaling이 "smarter"뿐 아니라 "more effective collaborator"를 동시에 만든다는 새로운 scaling proposition

## 관련 페이지

- thinking-machines — 발표 주체
- [omnimodality](/concepts/omnimodality.md) — modality 통합 일반론
- [openai-realtime-api](/tools/openai-realtime-api.md) — 직접 비교군
- [gemini-spark](/tools/gemini-spark.md) / [hyperclova-x-omni](/tools/hyperclova-x-omni.md) — 비교군
- [whisper-ecosystem](/tools/whisper-ecosystem.md) — encoder-free와 대비
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) — voice AI 패턴 일반
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — harness ↔ model 통합 흐름

## 출처

- VentureBeat, "Thinking Machines shows off preview of near-realtime AI voice and video conversation with new 'interaction models'" (2026-05-11) — Carl Franzen
- Thinking Machines blog, "interaction-models" (2026-05-11)
