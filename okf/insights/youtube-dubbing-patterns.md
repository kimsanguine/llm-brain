---
type: insight
title: YouTube 한국어 자막 더빙 파이프라인 패턴
tags:
- video-pipeline
- whisper
- gemini
- subtitle
timestamp: '2026-05-15'
x-llmbrain-domain:
- tools
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# YouTube 한국어 자막 더빙 파이프라인 패턴

## 핵심 원칙

YouTube 자막 더빙은 yt-dlp 다운로드 → [Whisper](/tools/whisper-ecosystem.md) 자막 생성 → Gemini 한국어 번역 → segment_edit.py 구간 편집의 4단계 파이프라인. 구간 제안 시 핵심 논지 먼저 파악 후 청중 관점에서 선택.

## 발견된 패턴

### 4원칙: 구간 편집 가이드라인 (2026-04-15)
1. **논지 먼저**: 사례 나열 전에 "핵심 논지"를 먼저 파악
2. **발화 끝에서 컷**: 구간 경계는 라운드 타임보다 발화 문단 — SRT 문맥 확인 후 문장 끝에서 컷 (±1~2분 조정 허용)
3. **번역 클러스터 재시도**: 1분 창에 3+ 연속 실패 시 재번역, 최종 저장 전 "잔존 ≤1% AND 클러스터 없음" 체크
4. **청중 관점 매칭**: 구간 제안 전 사용자 메모리에서 현재 과정 확인 → 관점 태깅 → 매칭 구간 우선

### Whisper 단독 실행 원칙 (2026-03-14, 2026-04-17)
- Whisper CPU 병렬 4개 실행 시 OS SIGTERM (메모리/CPU 경쟁)
- 단독 실행이 유일한 정답 (단독 시 CPU 31%, 4개 병렬 시 각 6~7%)
- faster-whisper small 단독 실행: 87분 영상을 13분 내 처리 (6.6x realtime)

### 2단계 결과물 전략 (2026-04-15)
- **빠른 초안**: `yt-dlp --write-auto-subs --skip-download` → VTT 즉시 확보 → ffmpeg VTT→SRT → Gemini 번역 (30분 내 초안)
- **최종 정식**: Whisper 전체 SRT 완성 후 동일 구간 재번역 → 품질 업그레이드
- 두 경로를 병행해 진행분 낭비 없음

### 번역 캐시 시스템 (2026-03-22, 2026-04-14)
- `translation_cache.json`으로 API 재호출 없이 타임스탬프만 교체
- 기존 `*_ko.srt`에서 캐시 자동 구축 (en/ko SRT zip 매칭)
- 완료 판정 기준: `videos/<id>/*_ko.srt` 존재 여부

### segment_edit.py 패턴 (2026-03-22, 2026-04-17)
- 다중 구간 = 합본 단일 파일. 개별 영상은 각 호출 후 src/ 이동 처리
- `_final` 덮어쓰기 / src 이동 이슈: 두 파트 연속 실행 시 rename + 복원 필요
- cleanup이 `_final`/`_ko` 없는 파일을 `src/`로 이동시킴 주의

### yt-dlp n challenge 우회 (2026-04-09)
- `best[ext=mp4]` 또는 format 18로 단일 파일 다운로드
- 특수문자 파일명(전각 `｜` `？` 포함) 경로는 bash sed 불가 → Python 필수

### FFmpeg SRT 타임코드 처리 (2026-04-17)
- `-ss before -i`: keyframe seek + 타임스탬프 자동 0 리셋 (상세: [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md))
- ffprobe로 추출 결과 검증 필수
- SRT 타임코드 시프트: `(원본시작 - 세그먼트시작) + 누적오프셋`

### 폴더 컨벤션 (2026-04-17)
- `{연사}_{주제}_Part{N}/` + `{snake_case}_final.mp4`
- 영상 ID 폴더는 임시 처리 후 삭제

### Gemini 429 재시도 패턴 (2026-03-14)
- `30 * (retry+1)` 점진적 대기 + 5회 재시도
- `BATCH_DELAY=4` 예방적 딜레이로 분당 15회 제한 회피

### 장시간 작업 모니터링 (2026-04-14)
- ScheduleWakeup으로 예상 완료 시점에 wake-up 예약 (폴링 대신)
- 프로세스 진단 3종: CPU/stdout/TCP 조합 (CPU 0% + TCP 활성 = 정상 대기)
- Python stdout 버퍼링: `PYTHONUNBUFFERED=1`로 실시간 로그 확인

## 적용 방법

1. **다운로드**: yt-dlp 또는 `--write-auto-subs` fast-path
2. **자막 생성**: Whisper 단독 실행 (병렬 금지)
3. **구간 선정**: 핵심 논지 파악 → 청중 관점 매칭 → 발화 끝 컷
4. **번역**: Gemini + 번역 캐시 + 잔존 재시도 체크
5. **검수**: "잔존 ≤1% AND 클러스터 없음" 기준 확인
6. **파일 정리**: 폴더 컨벤션 준수

## 관련 개념
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- til-patterns-2026-05
- [whisper-ecosystem](/tools/whisper-ecosystem.md)
- [youtube-subtitle-pipeline](/concepts/youtube-subtitle-pipeline.md)
- [ffmpeg-subtitle-pipeline](/concepts/ffmpeg-subtitle-pipeline.md)
- [remotion-video-patterns](/insights/remotion-video-patterns.md)
- [pptx-automation-patterns](/insights/pptx-automation-patterns.md)
