---
type: concept
title: YouTube 자막 파이프라인
description: 'YouTube 영상에서 한국어 자막을 생성하는 파이프라인의 두 가지 경로: yt-dlp fast-path(자동 자막, 빠름)와
  Whisper(STT 기반, 고품질).'
tags:
- yt-dlp
- whisper
- subtitle
- srt
- ffmpeg
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

# YouTube 자막 파이프라인

## 핵심 요약

YouTube 영상에서 한국어 자막을 생성하는 파이프라인의 두 가지 경로: yt-dlp fast-path(자동 자막, 빠름)와 Whisper(STT 기반, 고품질). 긴 영상은 두 단계로 나누어 빠른 초안과 최종 정식을 병행 운영하는 전략이 효율적이다.

## 상세 내용

### yt-dlp fast-path (자동 자막)

```bash
yt-dlp --write-auto-subs --sub-langs en --sub-format vtt --skip-download <URL>
```

- 100분대 영상도 몇 초 만에 자막만 다운로드
- ffmpeg로 VTT → SRT 변환 후 번역 파이프라인 투입 가능

### auto-subs 정제법

YouTube 자동 자막은 2줄 스크롤 구조 (윗줄 = 이전 블록 반복, 10ms짜리 더미 전환 블록 포함).

정제 방법:
1. 각 블록의 `text_lines[-1]`만 취함
2. duration < 50ms 블록 제거

결과: 블록 수 약 50% 감소, 의미 보존 (예: 6,475 → 3,234 블록, 112분 영상 기준).

### Whisper vs auto-subs 자막 단위 차이

| 항목 | Whisper | auto-subs |
|---|---|---|
| 블록 단위 | 문장 의미 덩어리 | 더 잘게 쪼개짐 |
| 타이밍 | 음성과 정확히 일치 | 문법 불완전 |
| 영어 잔존 | 재번역 후 0% 가능 | 구간 집중 발생 |
| 속도 | 느림 (CPU 기준 1배) | 빠름 (초단위) |

### 병렬 번역 전략 (긴 영상 2단계)

1. **1단계 (즉시)**: yt-dlp auto-subs로 빠른 초안 확보
2. **2단계 (완료 후)**: Whisper STT 완료 후 같은 구간 재번역으로 품질 업그레이드
→ 진행분·시간 낭비 없이 "빠른 초안 + 최종 정식" 두 단계 배포 가능

### Whisper CPU 경합 주의

- faster-whisper medium 모델 4개 동시 실행 시: 각 프로세스 CPU ~2GB RAM 경쟁
- OS가 SIGTERM으로 오래된 프로세스 강제 종료 가능
- CPU 기반 Whisper는 병렬 이득 없음 → **단독 순차 실행** 권장 (6.6x realtime, 87분 → 13분)

### 번역 실패 블록 분포 감시

Gemini 배치에서 "원문 유지" 로그가 구간에 집중되면 시청 중 영어 자막 벽 발생.

- 1분 창에 3개 이상 연속 실패 시 해당 구간만 슬라이스해 재번역
- 최종 저장 전 체크: "잔존 ≤1% AND 연속 3+ 클러스터 없음"

### 구간 경계 설정 원칙

`30:00-50:00` 같이 라운드 타임으로 자르면 문장 중간에 끊길 수 있음.

→ ±30초 SRT 문맥 확인 후 문장이 완결되는 지점까지 포함 or 그 전에서 컷. ±1~2분 자유 조정 허용.

## 관련 개념
- [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md)
- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
