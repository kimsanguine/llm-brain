---
type: concept
title: Neural TTS Evolution
description: 신경망 TTS는 분리형 파이프라인에서 end-to-end seq2seq, 병렬 생성, LLM·코덱 기반 스트리밍 합성으로 이동했다.
tags:
- voice-ai
- tts
- speech-synthesis
- alignment
- streaming
timestamp: '2026-06-09'
x-llmbrain-created: '2026-06-08'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Neural TTS Evolution

## 핵심 요약

신경망 TTS는 분리형 파이프라인에서 end-to-end seq2seq, 병렬 생성, LLM·코덱 기반 스트리밍 합성으로 이동했다. 세대가 바뀔 때마다 핵심 병목은 음질 자체보다 **텍스트-음성 정렬, 추론 지연, 화자 제어, 콘텐츠와 화자 스타일의 분리**였다.

## 작동 원리

### 1. Tacotron: end-to-end TTS의 출발점

Tacotron(2017)은 문자 시퀀스에서 스펙트로그램을 직접 생성하는 seq2seq + attention 구조를 제시했다. 텍스트 분석, 음향 모델, 보코더가 분리된 기존 파이프라인의 오류 누적을 줄이고, 텍스트-오디오 쌍만으로 학습하는 방향을 열었다.

핵심은 CBHG 인코더, attention 디코더, reduction factor다. 실무에서는 Tacotron 계열로 멜 스펙트로그램을 만들고 WaveNet/HiFi-GAN 같은 별도 보코더로 파형을 복원하는 2단계 구성이 오랫동안 표준이었다.

### 2. Glow-TTS: 병렬 생성과 MAS

Glow-TTS(2020)는 정규화 flow와 Monotonic Alignment Search(MAS)를 결합해 외부 aligner 없이 텍스트와 음성 잠재 표현 사이의 단조 정렬을 찾는다. 자기회귀 Tacotron 계열보다 빠른 병렬 합성이 가능하고, 긴 문장에서 단어 반복·누락을 줄이는 robust한 정렬을 제공한다.

이 전환의 의미는 TTS가 "자연스럽게 말하는가"에서 "실시간으로 안정적으로 말하는가"로 이동했다는 점이다. MAS는 이후 VITS 같은 end-to-end TTS의 핵심 구성요소로 이어진다.

### 3. CosyVoice 2: LLM + flow matching + streaming

CosyVoice 2(2024)는 LLM, speech token, chunk-aware flow matching을 결합한 스트리밍 zero-shot TTS 사례다. 텍스트 입력과 동시에 음성을 생성하는 bi-streaming 구조로 저지연 합성을 겨냥하고, instruction 기반 제어와 zero-shot 화자 복제를 하나의 모델 안에 묶는다.

현대 TTS의 경쟁력은 MOS만이 아니라 first-audio latency, speaker similarity, prompt controllability, 실시간 중단/재개 같은 대화형 제품 지표로 이동했다.

### 4. Voice cloning: speaker adaptation vs encoding

Neural Voice Cloning(2018)은 소수 샘플 음성 복제를 두 경로로 나눴다. speaker adaptation은 다화자 TTS 모델을 새 화자의 짧은 오디오로 미세조정해 품질을 높이고, speaker encoding은 별도 인코더가 화자 임베딩을 추론해 빠르게 새 화자를 추가한다. 전자는 프리미엄 보이스 품질, 후자는 저지연·저자원 배포에 유리하다.

AutoVC(2019)는 voice conversion을 정보 병목 문제로 다룬다. bottleneck이 화자 정보를 걸러내면 콘텐츠와 화자 스타일을 분리할 수 있고, target speaker embedding을 주입해 본 적 없는 화자로 변환할 수 있다. 이 관점은 "화자 임베딩을 어떻게 만들고 어디에 주입할 것인가"라는 현대 zero-shot TTS 설계의 기본 질문으로 이어진다.

## 활용 사례

- 음성 비서, 내비게이션, 오디오북: Tacotron 계열의 멜 스펙트로그램 + 보코더 구조가 기본 설명 모델이다.
- 콜센터, IVR, 게임 NPC: Glow-TTS/VITS 계열의 병렬 생성과 속도·피치 제어가 중요하다.
- 실시간 음성 에이전트, 라이브 통역, 개인화 더빙: CosyVoice 2류 LLM-TTS와 zero-shot cloning이 제품 비용과 latency를 바꾼다.
- 오디오북, 게임 NPC, 더빙 서비스: speaker adaptation과 encoding을 품질·생성 속도·화자 추가 비용 기준으로 조합한다.

## habix/강의와의 연결점

AI Human Module 5에서는 TTS를 "모델 이름 암기"가 아니라 세대별 병목으로 가르치는 편이 좋다. Tacotron은 end-to-end 통합, Glow-TTS는 정렬과 병렬화, CosyVoice 2는 LLM·코덱·스트리밍을 대표한다.

PM 관점의 토론 질문은 명확하다. 우리 제품에서 중요한 것은 자연스러움, 지연시간, 화자 복제, 다국어 안정성, 오남용 방지 중 무엇인가? 이 질문은 [voice-ai-stack](/concepts/voice-ai-stack.md) Layer 3 TTS 선택과 [ai-governance-verification](/concepts/ai-governance-verification.md)의 voice cloning 가드레일로 이어진다.

## 관련 개념

- [voice-ai-stack](/concepts/voice-ai-stack.md)
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md)
- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [omnimodality](/concepts/omnimodality.md)
- ai-paper-learning-path
- [ai-governance-verification](/concepts/ai-governance-verification.md)
