---
type: tool
title: MediaPipe & Google AI Edge 스택
description: MediaPipe는 모델이 아니라 파이프라인 프레임워크다.
tags:
- mediapipe
- google-ai-edge
- litert
- litert-lm
- edge-ai
timestamp: '2026-05-15'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 2
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# MediaPipe & Google AI Edge 스택

## 핵심 요약

MediaPipe는 모델이 아니라 파이프라인 프레임워크다. 2019년 Google Research에서 공개된 C++ 그래프 기반 실시간 인식 파이프라인으로, 2023년 Google AI Edge 조직으로 이동하면서 LiteRT, LiteRT-LM과 함께 엣지 AI 스택을 구성한다. [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md) 및 [omnimodality](/concepts/omnimodality.md) 맥락에서 함께 이해할 것.

## 상세 내용

### Google AI Edge 포트폴리오 (2026년 4월 기준)

| 레이어 | 이름 | 역할 |
|---|---|---|
| 런타임 (일반 ML) | LiteRT (구 TFLite) | 모델 추론 엔진 |
| 런타임 (LLM) | LiteRT-LM | Gemini Nano · Gemma용 엔진 |
| 프레임워크 | MediaPipe Framework | 그래프 기반 파이프라인 |
| 솔루션 | MediaPipe Solutions / Tasks | 완제품 레고 블록 (12종) |

### 3층 스택 구조

```
[사용자 앱]
     │
     ▼
┌─────────────────────────┐
│ MediaPipe Solutions     │  ← 완제품 (얼굴 12점, 손 21점, 포즈 33점...)
├─────────────────────────┤
│ MediaPipe Framework     │  ← 파이프라인 엔진 (calculator들을 엮는 곳)
├─────────────────────────┤
│  LiteRT (구 TFLite)     │  ← 텐서 연산 런타임
└─────────────────────────┘
```

비교 기준: "MediaPipe vs TFLite"가 아닌 "MediaPipe Solutions vs 직접 짜기"가 올바른 비교다.

### 주요 변화 (2024-2026)

**LLM Inference API 등장 (2024)**
- Gemma 2B, Phi-2, Falcon, Stable LM 등 지원
- Gemma 1.1 7B (8.6GB)까지 웹 브라우저 안에서 실행 가능
- 기술: 모델을 작은 청크로 분할 → 온디맨드 로딩 → 스트리밍 복사

**LiteRT-LM 분기 (2025)**
- TFLite → LiteRT 리브랜딩 + GPU/NPU 가속 강화
- LLM 전용 엔진 LiteRT-LM 분기
- Google 공식 권고: 온디바이스 LLM은 LiteRT-LM으로 마이그레이션
- Pixel Watch, Chromebook Plus, Chrome 내장: LiteRT-LM 사용

**Gemini Nano 엣지 착지 (2025-2026)**
- Pixel 폰, Pixel Watch, Chromebook Plus, Chrome 브라우저에 탑재
- Google 자사 제품에는 MediaPipe가 아닌 LiteRT-LM을 엔진으로 사용
- 멀티모달 처리 확장: [gemini-omni-flash](/tools/gemini-omni-flash.md)가 클라우드에서 담당하는 것을 엣지에서 일부 수행

### Physical AI 시장 맥락 (2026-04 기준)

- 시장 규모: 2026년 USD 1.50B → 2032년 USD 15.24B (CAGR 47.2%, MarketsandMarkets)
- 주요 진영: NVIDIA Jetson Thor (2000 TFLOPS), Qualcomm Dragonwing IQ10 (저전력), Arm (플랫폼 레이어), Apple (폐쇄 수직)
- MediaPipe의 포지션: 어느 칩에서나 비슷한 추상화로 돌아가는 오픈 레이어 ("Physical AI 시대의 쿼리 레이어")

### 락인 수준

- **솔루션 층**: 락인 낮음 (ONNX 변환 가능, Hugging Face Optimum 자동화)
- **프레임워크 층**: 락인 높음 (C++ 그래프 구조 이전 비용 큼)

### 사용 판단 기준

**권장 상황**
- 카메라 프레임에서 사람 관련 지표(얼굴/손/자세/제스처) 추출
- Android/iOS/Web/Python 4개 플랫폼 동시 배포
- ML 감각을 얻는 첫 도구

**마이그레이션 플래그 필요**
- 온디바이스 LLM 추론 → LiteRT-LM 이전 경로를 PRD에 미리 포함
- Image Generator (엔진 이전 중)

**비권장 상황**
- Jetson Thor 기반 로봇 앱 (NVIDIA Isaac + TensorRT 권장)
- 서버 측 실시간 비디오 파이프라인 (DeepStream 또는 GStreamer 권장)
- PyTorch 파이프라인과 강결합된 팀 (ONNX Runtime 권장)

## 관련 개념
- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md)
- [omnimodality](/concepts/omnimodality.md)
- [gemini-omni-flash](/tools/gemini-omni-flash.md)
