---
type: concept
title: Voice AI Stack
description: 음성 AI 시스템을 구성하는 4계층 아키텍처.
tags:
- voice-ai
- stt
- tts
- realtime
- synthesis-hub
timestamp: '2026-06-08'
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://thinkingmachines.ai/blog/interaction-models
- https://openai.com
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Voice AI Stack

음성 AI 시스템을 구성하는 4계층 아키텍처. 각 계층마다 선택지가 다르고, 계층 간 연결 방식이 시스템 전체 latency와 품질을 결정한다.

## 4-Layer Architecture

```
┌──────────────────────────────────┐
│  Layer 4: Full-Duplex Control    │  ← 200ms 동시성, turn-taking
├──────────────────────────────────┤
│  Layer 3: TTS                    │  ← 음성 출력
├──────────────────────────────────┤
│  Layer 2: LLM 추론               │  ← 의도 파악, 툴 호출, 응답 생성
├──────────────────────────────────┤
│  Layer 1: STT                    │  ← 음성 입력 → 텍스트
└──────────────────────────────────┘
```

기존 turn-based 시스템은 이 4계층을 **직렬**로 연결한다: 사용자 발화 완료 → STT → LLM → TTS → 응답. [interaction-models](/concepts/interaction-models.md)는 이 직렬 구조를 **동시 병렬 처리**로 전환한 첫 번째 native 구현이다.

---

## Layer 1: STT (Speech-to-Text)

사용자 음성을 텍스트로 변환하는 계층. [whisper-ecosystem](/tools/whisper-ecosystem.md)이 사실상의 기준점이다.

### 2026-06-05 보강: ASR의 본질은 정렬 없는 시퀀스 변환

AI Human paper raw의 RNN-T, attention-based ASR, NVIDIA Canary 묶음은 STT layer의 핵심 문제가 "입력 음성과 출력 토큰 길이가 다르고 정렬 정보가 없는 sequence transduction"임을 보여준다. RNN-T는 transcription network와 prediction network를 결합해 CTC의 조건부 독립 가정을 줄이고, 스트리밍 ASR의 표준 구조가 됐다.

Attention-based ASR은 기계번역식 attention을 음성에 그대로 적용하면 긴 입력에서 정렬이 무너진다는 점을 보여준다. location-aware/monotonic 설계가 필요한 이유다. 2024 Canary는 FastConformer와 data balancing, dynamic blending, noise-robust fine-tuning으로 적은 데이터에서도 ASR+speech translation 성능을 끌어올린 사례다.

### 2026-06-06 보강: 종단간 ASR의 동력은 규모와 데이터 품질

paper raw(Deep Speech 2 / SpecAugment / OWSM v4)는 STT layer의 발전 동력이 정교한 파이프라인이 아니라 **규모(데이터·연산) + 데이터 품질**로 이동했음을 보여준다(raw 원문 기준). Deep Speech 2(2015)는 음향 모델·발음 사전·HMM으로 나뉘던 전통 ASR을 CTC 단일 신경망으로 통합해 영어/만다린을 같은 구조로 인식했고, "스케일이 곧 성능"의 출발점이 됐다. SpecAugment(2019)는 로그 멜 스펙트로그램에 time warp·frequency/time mask를 적용하는 음성판 표준 증강으로, Whisper·Conformer·wav2vec 학습 레시피에 거의 기본 탑재됐다. OWSM v4(2025)는 Whisper를 완전 공개 데이터·코드로 재현하며 재정렬→LID 필터→CTC 신뢰도 필터 3단계 클리닝만으로 평균 WER 8.12%→7.44%를 달성, 병목이 모델 구조가 아니라 데이터 품질로 이동했음을 정량 입증한다. [whisper-ecosystem](/tools/whisper-ecosystem.md)의 production 분기, ai-paper-learning-path Module 4-5 음성 계보와 연결된다.

### 주요 구현 비교

| 구현 | 제작 | 특징 | 적합 상황 |
|---|---|---|---|
| OpenAI Whisper (원본) | OpenAI | MIT 라이선스, 99개 언어 | 연구·기준점 |
| faster-whisper | SYSTRAN | CTranslate2, 4배 빠름, 메모리 절반 | 속도 우선 production |
| distil-whisper | HuggingFace | Knowledge Distillation, 6배 빠름, 49% 작음 | 엣지·모바일 |
| WhisperX | 옥스퍼드 연구자 | 단어 단위 타임스탬프 + 화자 분리 | 회의록, 다자 대화 |
| ElevenLabs Scribe | ElevenLabs | 96.7% 정확도, $0.40/시간 | 정확도 SLA 필요 |
| GPT-Realtime-Whisper | OpenAI | 스트리밍 실시간, $0.017/분 | 음성 에이전트 연속 입력 |

**엣지 STT**: [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)의 LiteRT-LM이 온디바이스 STT 실행을 지원. distil-whisper를 Gemma Nano와 결합하는 경로가 2026년 기준 표준 엣지 스택으로 부상 중.

---

## Layer 2: LLM 추론

STT 결과를 받아 의도를 파악하고, 툴을 호출하거나 응답 텍스트를 생성하는 계층.

### 음성 AI에서의 추론 설계 원칙

- **reasoning_effort 선택**: [openai-realtime-api](/tools/openai-realtime-api.md)의 GPT-Realtime-2는 minimal~xhigh 5단계. 단순 Q&A는 `low`, 복잡한 agentic 흐름은 `high`/`xhigh`.
- **Parallel tool calls**: 음성 에이전트는 툴 호출 중에도 "checking your calendar…" 같은 backchannel을 동시에 내보내야 UX가 자연스럽다.
- **컨텍스트 윈도우 비용**: GPT-Realtime-2는 128K 토큰 지원하지만 오디오 토큰 비용($32/$64/1M)이 높아 긴 세션은 비용 설계 필수.

---

## Layer 3: TTS (Text-to-Speech)

LLM 응답 텍스트를 음성으로 변환하는 계층.

### 2026-06-07 보강: TTS의 세대 전환은 정렬과 지연시간의 역사

paper raw(Tacotron / Glow-TTS / CosyVoice 2)는 TTS 진화를 "분리형 파이프라인 → end-to-end seq2seq → 병렬 flow 생성 → LLM·코덱 기반 스트리밍"으로 정리한다. Tacotron은 문자에서 스펙트로그램을 직접 생성해 end-to-end TTS를 열었고, Glow-TTS는 MAS로 외부 aligner 없이 단조 정렬을 찾아 병렬 합성을 가능하게 했다. CosyVoice 2는 LLM, speech token, chunk-aware flow matching을 결합해 zero-shot 화자 복제와 양방향 스트리밍을 같은 시스템에 묶는다.

실무 선택 기준도 바뀐다. TTS 품질은 MOS 하나로 끝나지 않고 first-audio latency, speaker similarity, prosody controllability, instruction following, voice owner consent까지 함께 평가해야 한다. 세대별 상세는 [neural-tts-evolution](/concepts/neural-tts-evolution.md)에서 정리한다.

### 주요 구현 비교

| 구현 | 특징 | 비고 |
|---|---|---|
| ElevenLabs | voice cloning, 감정 표현, 낮은 latency | 상용 표준 |
| OpenAI TTS | 6개 음성, 저렴한 가격 ($15/1M chars) | 빠른 통합 |
| Gemini TTS (Google) | 한국어 포함 다국어, 자연스러운 억양 | 260203_longform_agent 기본 엔진 |
| Qwen3-TTS | 한국어 특화 voice cloning | 로컬 fallback 옵션 |
| DeepBrain AI Context-Aware TTS | 문장부호·구문·의미 맥락 기반 자동 prosody 조정, 1,000+ 보이스 | 교육·미디어·공공용 보이스 디렉션 |
| Raon-OpenTTS | DiT 기반 오픈 데이터·가중치·학습 파이프라인, 0.3B~1B 모델 | 오픈 웨이트 TTS 실험·재현 |
| VoxCPM2 | 토크나이저 없이 연속 음향 표현을 직접 모델링, 2B·30개 언어·48kHz | 오픈 TTS와 보이스 디자인 실험 |
| X-Voice | F5-TTS 확장, 언어 ID 이중 주입, 전사문 없는 30개 언어 zero-shot voice cloning | 크로스링구얼 보이스 클로닝 |
| ElevenLabs Music v2 | 장르 전환·보컬·사운드 이펙트를 자연어 조건으로 생성 | TTS에서 오디오 생성 풀스택으로 확장 |
| 온디바이스 TTS | LiteRT-LM 기반, 네트워크 불필요 | 엣지 음성 에이전트 |

### Voice cloning UX / guard rail

2026-05-28 브리프의 Spotify Studio와 ElevenLabs ALS 사례는 TTS 계층이 단순 낭독 엔진이 아니라 **개인 정체성·신뢰·동의**를 다루는 제품 계층임을 보여준다.

- Spotify Studio: 이메일·캘린더·웹·PDF 컨텍스트를 개인용 팟캐스트로 합성. 출력 voice selection이 신뢰 UX의 핵심이 된다.
- ElevenLabs ALS voice restoration: 16초 음원으로 개인 목소리 복원. 접근성 가치가 크지만, 본인 동의·인증·회수 가능성 없이는 오남용 리스크가 크다.

따라서 음성 제품의 TTS 레이어에는 최소 3개 가드레일이 필요하다: voice owner consent, voice sample provenance/authentication, generated voice revoke/delete flow.

### Context-aware prosody와 voice direction

2026-05-29 브리프의 DeepBrain AI Context-Aware Expressive TTS는 TTS 제어면이 **감정 라벨 선택**에서 **문맥 기반 prosody 추론**으로 이동 중임을 보여준다. 보이스 PM/디렉터가 지정해야 할 것은 "기쁨 70%" 같은 태그보다 더 구체적인 발화 목적이다.

- 대본의 정보 구조: 어디가 핵심 주장이고 어디가 부연인지
- 페르소나와 채널: 강의, 뉴스, 공공 안내, 광고의 신뢰 톤 차이
- 금지 톤: 과장, 조롱, 과도한 친밀감, 의료·금융 영역의 불필요한 감정 표현
- 검수 기준: WER뿐 아니라 prosody consistency, listener trust, correction workflow

Raon-OpenTTS처럼 데이터·가중치·학습 파이프라인까지 공개된 모델은 TTS를 API 호출 기능이 아니라 사내 음성 브랜드 자산으로 fine-tune하거나 평가할 수 있는 선택지를 만든다.

### Tokenizer-free와 cross-lingual cloning

2026-05-30 브리프의 VoxCPM2와 X-Voice는 TTS 품질 경쟁이 보코더 교체를 넘어 **표현 단위와 조건 주입 방식** 경쟁으로 이동했음을 보여준다. VoxCPM2는 별도 오디오 토크나이저 없이 연속 음향 표현을 직접 모델링해 토큰화 손실을 줄이고, 텍스트 설명만으로 새 보이스를 설계하는 voice design을 지원한다. X-Voice는 F5-TTS를 확장해 언어 ID를 임베딩·어텐션 양쪽에 주입하고, 오디오 프롬프트 전사문 없이 30개 언어 zero-shot cloning을 목표로 한다.

제품 판단 포인트는 세 가지다: 한국어 TTS 파이프라인을 통합 모델로 확장하려면 다국어·화자·스타일이 균형 잡힌 데이터가 먼저 필요하고, 아키텍처는 이산 오디오 토큰과 연속 잠재 표현 중 어느 손실을 감수할지 선택해야 하며, 평가는 WER/SIM만으로 부족해 cross-lingual speaker consistency와 prompt controllability를 같이 봐야 한다.

---

## Layer 4: Full-Duplex Control (200ms 동시성)

4계층 중 가장 최근에 등장한 계층. turn-based 시스템에는 존재하지 않는다.

### Turn-based vs Full-duplex

| 구분 | Turn-based | Full-duplex |
|---|---|---|
| 처리 방식 | 직렬 (완료 대기 → 처리 → 응답) | 동시 (200ms chunk 병렬) |
| 사용자 경험 | 질문을 이메일처럼 정제해야 함 | 자연스러운 대화 흐름 |
| 인터럽션 | 불가 또는 재시작 | 중간 interject 가능 |
| backchannel | 없음 | "I see", "mm-hmm" 실시간 |
| turn-taking latency | 0.57s~1.18s (현재 frontier) | 0.40s (TML-Interaction-Small) |

[interaction-models](/concepts/interaction-models.md)의 핵심 기여: 200ms chunk로 listen·talk·see를 동시 처리하고, 사용자가 말하는 동안에도 시각 단서를 감지해 proactive interject할 수 있다.

---

## 구현 경로: Cloud vs Edge

### Cloud Stack (표준)

```
사용자 마이크
  → GPT-Realtime-Whisper (STT, $0.017/분)
  → GPT-Realtime-2 / LLM API (추론)
  → ElevenLabs / OpenAI TTS (음성)
  → 스피커
```

장점: 빠른 통합, 고품질 모델. 단점: 네트워크 의존, 비용 누적, 프라이버시.

### Edge Stack

```
사용자 마이크
  → distil-whisper on LiteRT-LM (온디바이스 STT)
  → Gemma Nano on LiteRT-LM (온디바이스 LLM)
  → 온디바이스 TTS
  → 스피커
```

[mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)의 LiteRT-LM이 런타임 역할. 장점: 오프라인, 프라이버시 보장, 낮은 운영비. 단점: 모델 성능 제약.

**Physical AI 맥락**: 제조·의료·로봇 환경에서 네트워크 없이 작동하는 음성 인터페이스 수요가 CAGR 47.2% 성장 (2026-2032, MarketsandMarkets). 엣지 스택의 실용화 시점.

---

## OpenAI Realtime vs Thinking Machines Interaction Models

두 시스템은 서로 다른 계층 전략을 취한다.

| 비교 항목 | OpenAI Realtime API | TML Interaction Models |
|---|---|---|
| 아키텍처 | 기존 GPT-5급 모델 + Realtime 인터페이스 레이어 | 처음부터 full-duplex native 설계 |
| STT 방식 | GPT-Realtime-Whisper (별도 모듈) | encoder-free early fusion (dMel 직접 입력) |
| turn-taking latency | 1.18s (min) | 0.40s |
| Interaction Quality | 46.8 | 77.8 |
| 공개 여부 | 일반 공개, API 제공 | Research preview, 미공개 |
| 주요 강점 | 생태계·통합 용이성, 70+ 언어 번역 | 자연스러운 동시성, 시각 단서 proactive interject |

OpenAI Realtime은 **레이어 조합(기존 모델 + 인터페이스)**이고, [interaction-models](/concepts/interaction-models.md)은 **레이어 통합(모델 안에 전 계층 내재화)**이다. 이 차이가 latency와 품질 gap의 원인이다.

---

## 관련 개념

- [whisper-ecosystem](/tools/whisper-ecosystem.md) — Layer 1 STT 전체 생태계 (faster-whisper·WhisperX·Scribe 비교)
- [neural-tts-evolution](/concepts/neural-tts-evolution.md) — Layer 3 TTS의 세대별 정렬·지연·화자 제어 계보
- [openai-realtime-api](/tools/openai-realtime-api.md) — Layer 2-3 cloud 표준 구현, 3종 모델 (Realtime-2·Translate·Whisper)
- [interaction-models](/concepts/interaction-models.md) — Layer 4 full-duplex native 구현, Thinking Machines Lab
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) — 음성 AI 3패턴 (Voice-to-action·Systems-to-voice·Voice-to-voice)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) — 엣지 스택 런타임 (LiteRT-LM, distil-whisper on-device)
- [hyperclova-x-omni](/tools/hyperclova-x-omni.md) — 부착형 omnimodal 구현 사례 (STT+VLM+TTS 조합)
- [gemini-omni-flash](/tools/gemini-omni-flash.md) — 통합형 omnimodal 구현 사례 (cloud 기반)
- [mira-murati](/people/mira-murati.md) — Thinking Machines Lab 창립자, Interaction Models 발표 주도
- thinking-machines — Interaction Models 발표 주체, research-first frontier lab
- [omnimodality](/concepts/omnimodality.md) — modality 통합 일반론 (부착형 vs 통합형 경로)
