---
type: tool
title: OpenAI Realtime API
description: 2026-05-07 OpenAI가 Realtime API에 음성 모델 3종을 출시했다.
tags:
- openai
- realtime
- voice
- stt
timestamp: '2026-05-16'
x-llmbrain-domain: AI/LLM
x-llmbrain-created: '2026-05-16'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# OpenAI Realtime API

## 핵심 요약

2026-05-07 OpenAI가 Realtime API에 음성 모델 3종을 출시했다. GPT-Realtime-2는 GPT-5급 추론을 실시간 음성에 결합한 첫 번째 모델이며, GPT-Realtime-Translate는 70개 이상 언어의 실시간 번역, GPT-Realtime-Whisper는 저지연 스트리밍 STT를 제공한다. 음성이 단순 call-and-response에서 벗어나 실제 작업을 수행하는 인터페이스로 전환되는 신호다.

## 주요 기능

### GPT-Realtime-2

GPT-5급 추론을 실시간 음성 인터페이스에 결합한 모델.

| 기능 | 설명 |
|---|---|
| Preambles | 응답 전 "let me check that" 식 문구로 처리 중임을 알림 |
| Parallel tool calls | 병렬 툴 호출 + "checking your calendar" 가청 알림 |
| Recovery behavior | 실패 시 "I'm having trouble with that" 자연스러운 복구 |
| Context window | 32K → **128K** 확장 |
| Reasoning effort | minimal / low / **medium** / high / xhigh (기본: low) |
| Tone control | 상황별 톤 조절 (차분·공감·활기) |

**벤치마크** (vs GPT-Realtime-1.5):
- Big Bench Audio: **+15.2%** (high 레벨)
- Audio MultiChallenge: **+13.8%** (xhigh 레벨)

**가격**: $32/1M 입력 토큰 ($0.40 캐시) · $64/1M 출력 토큰

---

### GPT-Realtime-Translate

70+ 입력 언어 → 13 출력 언어를 화자 속도에 맞춰 실시간 번역.

**파트너 사례**:
- Deutsche Telekom: 고객이 편한 언어로 말하고 AI가 번역
- BolnaAI: 힌디어·타밀어·텔루구어 WER **12.5% 감소**
- Vimeo: 제품 교육 영상 실시간 다국어 번역

**가격**: $0.034/분

---

### GPT-Realtime-Whisper

말하는 동시에 전사하는 저지연 스트리밍 STT.

**용도**: 회의·교실·방송 실시간 캡션, 고객 지원·의료·영업 후속 워크플로우.

**가격**: $0.017/분

## 사용 패턴

세 가지 음성 AI 패턴에 각각 대응:
- **Voice-to-action** → GPT-Realtime-2 (추론 + 툴 호출)
- **Voice-to-voice** → GPT-Realtime-Translate (다국어 번역)
- 실시간 전사 → GPT-Realtime-Whisper

복합 패턴: Priceline은 항공·호텔 검색, 일정 변경, 현지 번역을 단일 음성 세션으로 처리.

reasoning_effort를 `low`(기본)로 두면 단순 인터랙션 지연 최소화, `high`/`xhigh`는 복잡한 agentic 흐름에 사용.

## 주의사항 / 함정

- `reasoning_effort=xhigh`는 벤치마크 최상위지만 지연 비용이 있음 — 단순 Q&A에는 과잉
- 컨텍스트 128K로 늘었지만 토큰당 오디오 비용($32/$64)이 높아 긴 세션은 비용 계산 필수
- GPT-Realtime-Whisper는 오프라인 Whisper 대비 정확도 비교 데이터 미공개 — 생산 투입 전 직접 WER 측정 권장
- EU Data Residency 지원하나 기본값은 아님 — 유럽 배포 시 명시적 설정 필요

## 관련 도구

- [whisper-ecosystem](/tools/whisper-ecosystem.md) — 오프라인 Whisper 생태계 (faster-whisper, distil-whisper, WhisperX, ElevenLabs Scribe)
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — 멀티 에이전트 패턴 (음성 에이전트 팀 구성 참고)
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) — Voice-to-action / Systems-to-voice / Voice-to-voice 3패턴 상세
