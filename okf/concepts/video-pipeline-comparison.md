---
type: concept
title: Video Pipeline Tools 비교
description: 각 단계의 함정·실무 패턴은 본 wiki에서 자세히 다룸.
tags:
- video
- pipeline
- comparison
- synthesis-hub
- ffmpeg
- subtitle
timestamp: '2026-05-26'
x-llmbrain-domain:
- tools
- video
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://www.remotion.dev
- https://ffmpeg.org
- https://github.com/openai/whisper
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

## 비디오 파이프라인 단계별 도구

| 단계 | 대표 도구 | 본 wiki 페이지 |
|---|---|---|
| **자막 추출 (STT)** | Whisper / faster-whisper / WhisperX / ElevenLabs Scribe | [whisper-ecosystem](/tools/whisper-ecosystem.md) |
| **자막 합성/렌더** | FFmpeg (libass) / FFmpeg drawtext | [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md) |
| **YouTube 자막 자동화** | yt-dlp + Whisper 2단계 | [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md) |
| **더빙·번역 자막** | Whisper + LLM 번역 + 구간 편집 | [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md) |
| **프로그래밍 비디오 생성** | Remotion (React + Puppeteer 렌더) | [remotion-video-patterns](/insights/remotion-video-patterns.md) |
| **엣지·실시간 비전** | MediaPipe / LiteRT / LiteRT-LM | [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) |
| **omnimodal 영상 (생성+편집)** | Gemini Omni Flash / Sora / Seedance | [gemini-omni-flash](/tools/gemini-omni-flash.md) |

## 도구 선택 매트릭스

### "어떤 도구를 언제 쓰나"

| 시나리오 | 선택 |
|---|---|
| 한국어 long-form 콘텐츠 자막 | [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md) (yt-dlp fast-path + Whisper 2단계) |
| 자막 슬라이싱·렌더 | [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md) |
| YouTube 더빙 (한국어→영어) | [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md) + Whisper |
| 프로그래밍적 영상 (인포그래픽 등) | [remotion-video-patterns](/insights/remotion-video-patterns.md) |
| 실시간 비전 (사람 감지·자세) | [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) |
| 영상 생성 (text-to-video) | [gemini-omni-flash](/tools/gemini-omni-flash.md) (단, Seedance 2.0이 단독 영상 품질 우위) |

## 주요 함정 비교

- **FFmpeg `-ss` before `-i`**: 빠르지만 keyframe seek (정확도 trade-off). 자세한 내용: [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md)
- **Whisper-only vs WhisperX**: 화자 분리 필요하면 WhisperX, 단순 자막은 faster-whisper. [whisper-ecosystem](/tools/whisper-ecosystem.md)
- **Remotion 렌더 시간 vs FFmpeg 합성**: 단순 자막은 FFmpeg, 인터랙티브 visual은 Remotion. [remotion-video-patterns](/insights/remotion-video-patterns.md)
- **온디바이스 추론 (LiteRT-LM 마이그레이션)**: [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) 참조

## 통합 워크플로 예시

```
YouTube URL
   ↓ yt-dlp
원본 영상
   ↓ Whisper (faster-whisper / WhisperX)
영문 자막 (.srt)
   ↓ LLM 번역 (Claude / GPT)
한국어 자막 (.srt)
   ↓ FFmpeg libass
자막 burn-in 영상
   ↓ (선택) Remotion에서 추가 visual 합성
최종 영상
```

각 단계의 함정·실무 패턴은 본 wiki에서 자세히 다룸.

## 본 wiki 차세대 방향

- Whisper API → on-device LiteRT-LM Whisper (지연 ↓, 비용 ↓)
- Gemini Omni Flash 같은 omnimodal 모델로 자막 + 영상 생성 통합
- Remotion + LLM 콘텐츠 자동 생성 파이프라인

## 관련 개념

- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md)
- [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md)
- [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md)
- [remotion-video-patterns](/insights/remotion-video-patterns.md)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md)
- [gemini-omni-flash](/tools/gemini-omni-flash.md)
- [realtime-voice-ai-patterns](/concepts/realtime-voice-ai-patterns.md)
