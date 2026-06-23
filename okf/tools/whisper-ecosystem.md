---
type: tool
title: Whisper 생태계
description: OpenAI Whisper는 레퍼런스 구현(reference implementation)이다.
tags:
- whisper
- openai
- stt
- speech-recognition
timestamp: '2026-05-29'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Whisper 생태계

## 핵심 요약

OpenAI Whisper는 레퍼런스 구현(reference implementation)이다. production 인프라를 들고 있는 건 SYSTRAN, HuggingFace, ElevenLabs, 그리고 개별 연구자들이다. "오픈소스를 만든 회사가 그 오픈소스의 주인은 아닐 수 있다."

## 상세 내용

### OpenAI Whisper 원본

- 공개: 2022년 9월, MIT 라이선스 (코드 + 모델 모두 공개)
- 학습 데이터: 68만 시간(약 78년치) 다국어 음성
- 지원 언어: 99개
- 모델 크기: tiny(39MB) / base(74MB) / small(244MB) / medium(769MB) / large(1.55GB)
- 한계: CPU에서 1시간 영상 처리에 ~1시간 소요. large-v3 VRAM 10GB+ 요구

### 4개 핵심 fork / 파생

**SYSTRAN/faster-whisper**
- 제작: 프랑스 SYSTRAN (1968년 설립, 기계번역 전문)
- 기술: CTranslate2 추론 엔진 위에 Whisper 재구현
- 성능: 같은 정확도로 최대 4배 빠름, 메모리 절반
- 8-bit 양자화 옵션으로 추가 가속 가능
- 현재 production 회의록 SaaS 상당수가 이 fork 사용

**huggingface/distil-whisper**
- 제작: HuggingFace 직접 개발
- 기술: Knowledge Distillation으로 모델 압축
- 성능: 6배 빠르고, 49% 작고, WER(단어 오류율) 1% 이내 손실
- 활용: 엣지 디바이스(모바일·임베디드), 차량 인포테인먼트

**m-bain/WhisperX**
- 제작: 영국 옥스퍼드 박사과정생
- 기능: 원본 Whisper + 단어 단위 타임스탬프 + 화자 분리(speaker diarization)
- 활용: "이건 김 매니저, 이건 박 디렉터" 화자 구분 회의록 SaaS의 핵심 기반

**ElevenLabs Scribe**
- 공개: 2025년 2월
- 성능: 영어 96.7% 정확도, 99개 언어, 1파일 32명까지 화자 분리
- 자체 벤치마크: Whisper v3 / Gemini 2.0 Flash / Deepgram Nova-3 대비 우위 주장
- 인도네시아어: Whisper v3 WER 7.7% → Scribe 2.4%
- 가격: 시간당 $0.40

### production 스택 선택 가이드

| 목적 | 권장 스택 |
|---|---|
| 속도 우선 | faster-whisper (SYSTRAN) |
| 화자 분리 필요 | WhisperX |
| 엣지/모바일 | distil-whisper |
| 정확도 SLA 필요 | ElevenLabs Scribe |
| 학습/연구 기준점 | OpenAI Whisper 원본 |

### 로컬 우선 받아쓰기 패턴 — OpenWhispr

2026-05-28 브리프는 OpenWhispr v1.7.1을 로컬 우선 STT 사례로 기록했다. OpenWhispr는 OpenAI Whisper와 NVIDIA Parakeet을 로컬에서 실행하고, 필요할 때만 사용자의 API key로 클라우드 모델에 우회하는 BYOK 구조다. macOS 마우스 버튼 단축키, 로컬 전사 묵음 처리 개선, Windows 로컬 Whisper 복구 같은 실사용 개선이 포함됐다.

제품적으로는 [voice-ai-stack](/concepts/voice-ai-stack.md)의 STT Layer에서 **local-first + cloud fallback**이 개인정보 민감 도메인의 기본 패턴이 될 수 있음을 보여준다. 의료·법무·교육처럼 음성 원본 유출 리스크가 큰 영역에서는 클라우드 품질보다 로컬 추론 경로와 데이터 보관 정책이 우선이다.

### 음성 인식 시장 (2024-2030)

- 2024년: USD 8.49B (약 11조 원)
- 2030년 전망: USD 23.11B (약 30조 원), CAGR 19.1%
- 클라우드 배포 62% 압도적, 모바일·엣지 비중 빠르게 증가
- 비교 벤치마크 기준: 거의 모두 "OpenAI Whisper보다 얼마나 빠른/정확한가"

### Whisper 무음 블록 보정

Whisper가 무음 구간에서 잘못된 블록을 생성하는 현상 → 후처리 단계에서 duration이 매우 짧은 블록(< 50ms) 필터링 권장.

### GPT-Realtime-Whisper (2026-05-07 추가)

OpenAI의 스트리밍 STT API 버전. 오프라인 Whisper와 달리 화자가 말하는 동시에 실시간 전사.

- **차이점**: 오프라인 Whisper는 파일 완성 후 처리, GPT-Realtime-Whisper는 청크 단위 스트리밍
- **용도**: 회의 캡션, 이벤트 실시간 자막, 음성 에이전트 연속 입력
- **가격**: $0.017/분 (오프라인 Whisper 자체 호스팅보다 비용 높으나 인프라 불필요)
- **주의**: 공개 WER 비교 데이터 없음 — production 투입 전 직접 측정 권장
- 자세한 내용: [openai-realtime-api](/tools/openai-realtime-api.md)

## 관련 개념
- [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md)
- [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)
- [openai-realtime-api](/tools/openai-realtime-api.md) — GPT-Realtime-Whisper 포함 Realtime API 3종 모델
