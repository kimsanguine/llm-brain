---
type: concept
title: FFmpeg 자막 처리 패턴
description: FFmpeg를 사용한 영상 편집 및 자막 처리 시 알아야 할 핵심 동작 패턴.
tags:
- ffmpeg
- srt
- subtitle
- pipeline
timestamp: '2026-05-15'
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

# FFmpeg 자막 처리 패턴

## 핵심 요약

FFmpeg를 사용한 영상 편집 및 자막 처리 시 알아야 할 핵심 동작 패턴. `-ss` 위치에 따른 타임스탬프 리셋, `time=` 출력의 실제 의미, SRT 슬라이싱 방법을 포함한다. [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md) 실제 적용 사례와 함께 참고할 것.

## 상세 내용

### `-ss` before `-i` 타임스탬프 동작

```bash
# 권장 (keyframe fast seek + 타임스탬프 0 리셋)
ffmpeg -ss 00:10:00 -i input.mp4 -t 00:20:00 output.mp4

# 비권장 (정확하지만 느림)
ffmpeg -i input.mp4 -ss 00:10:00 -t 00:20:00 output.mp4
```

- `-ss`를 `-i` 앞에 두면: keyframe fast seek + 타임스탬프 0 리셋 자동 처리
- ffprobe `start_time ≈ 0`, `duration = 지정 길이`로 정확히 추출됨

### `time=` 출력의 의미

ffmpeg 스트림 복사(`-c copy`) 시 진행 표시의 `time=`은 output container의 PTS(Presentation Timestamp) 기반.

- 원본 기준일 수 있어 실제 길이와 다를 수 있음
- 실제 길이 확인: `ffprobe -v error -show_entries format=duration <file>`

### SRT 슬라이싱 패턴

합본 번역 SRT(0~35분)를 특정 기준 시간으로 분리하는 방법:

```python
from datetime import timedelta

# timedelta 기반으로 기준 시간(예: 20분) 이전/이후 블록 분리
# 분리된 블록의 타임스탬프에 offset 조정 필수
```

- `translation_cache.json` 활용 시 Gemini API 재호출 없이 즉시 재활용 가능

### segment_edit.py 다중 구간 동작

- 여러 구간 인자 → 합본 단일 영상 생성 (설계 의도)
- 별도 영상 원할 때: 각 구간을 개별 호출
- 주의: 첫 실행 후 원본이 `src/`로 이동 → 두 번째 호출 시 "원본 없음" 오류 발생

### youtube_dubbing 폴더 컨벤션

```
{연사}_{주제키워드}/
├── {snake_case_제목}_final.mp4
├── {snake_case_제목}_ko.srt
└── src/          ← 원본 보관
    archive/      ← 캐시 보관
```

- 영상 ID 폴더(예: `We7BZVKbCVw`)는 임시 처리 공간 → 최종 완료 후 삭제
- 브라우저 기반 [remotion-video-patterns](/insights/remotion-video-patterns.md) 파이프라인과 달리 FFmpeg는 서버 사이드 처리에 최적화

### SRT 타임코드 시프트

```python
# 타임코드를 일정 시간만큼 이동시키는 공식
offset = timedelta(seconds=start_seconds)
new_start = original_start - offset
new_end = original_end - offset
```

## 관련 개념
- [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md)
- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md)
- [remotion-video-patterns](/insights/remotion-video-patterns.md)
