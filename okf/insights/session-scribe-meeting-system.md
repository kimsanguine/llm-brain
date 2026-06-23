---
type: insight
title: Session Scribe 회의 자동화 시스템 패턴
tags:
- meeting
- workflow-pattern
- whisper
- obsidian
- notion
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

# Session Scribe 회의 자동화 시스템 패턴

## 핵심 원칙

`/meeting` + `/meeting_end` 슬래시 커맨드로 회의 전사 → 요약 → Notion 저장의 엔드투엔드 파이프라인. 세션 식별자 관리와 Notion 중복 제목 방지가 핵심 취약 지점.

## 발견된 패턴

### 시스템 구성 (2026-03-15)
- `session_scribe.py`: start/join/note/stop/get_dir/save_notion/retry 서브커맨드
- `audio_scribe.py`: Zoom/Meet/대면 오디오 자동 캡처 (BlackHole + Whisper turbo)
- `calendar_trigger.py`: Google Calendar 2분 폴링 → 자동 세션 시작/종료/알림
- LaunchAgent 등록으로 상시 실행

### find_session_dir 3차 fallback 패턴 (2026-03-17)
- 1차: 폴더명 직접 탐색
- 2차: `meta.json`의 `session_name`으로 재탐색
- 3차: `--dir` 옵션으로 경로 직접 지정
- 폴더 리네이밍 후 lookup 오류 시 fallback 3차 패턴 적용

### Notion 중복 제목 방지 (2026-03-17)
- 세션별 고유 제목 포맷: `topic (날짜)` 형식 사용
- 동일 이름 리소스 여러 개일 때 `--dir` 파라미터로 경로 직접 지정

### 회의 TIL 로그 형식 (2026-03-16~03-30)
```
### HH:MM 미팅명
- 주제: ...
- 핵심개념: N개
- 액션아이템: N개
- Notion: https://...
- 로컬: /path/to/session_summary.md
```
- Notion 저장 실패 시 `저장 실패 (세션 리네이밍 후 lookup 오류)` 명시

### 버그 수정 문서화 패턴 (2026-03-17)
- 소스 docstring + COMMANDS.md + README.md 3종 동시 업데이트
- 단일 문서만 업데이트하면 정합성 손실

### audio_scribe 장애 대응 패턴 (2026-03-20)
- NumPy < 2.4 고정 필수 (버전 호환성)
- `os.kill(pid, 0)` 패턴으로 프로세스 생존 확인
- WhisperModel 캐싱으로 재로드 시간 단축
- Claude Code 자동 트리거 우회 패턴 필요

### 회의 세션 활용 사례 (2026-03-16~03-31)
- 강의 세션 전사: 판다스 데이터프레임 활용 / 확률통계 / 이진분류 / 머신러닝 성능 평가
- 실무 세션: 도커/K3D/쿠버네티스 설치 / AI 서비스 배포
- 체크포인트 회의: Notion 기록 완료 시 핵심개념 0개로 기록

### ScheduleWakeup 장시간 작업 모니터링 (2026-04-14)
- 폴링 대신 예상 완료 시점에 wake-up 예약
- 프로세스 진단 3종: CPU / stdout / TCP 조합

## 적용 방법

1. **세션 시작**: `/meeting` 실행 → `session_scribe.py start` 자동 호출
2. **전사 확인**: 10청크 체크포인트 + `status` 서브커맨드로 진행 상황 모니터링
3. **세션 종료**: `/meeting_end` → 요약 생성 → Notion 저장 시도
4. **Notion 실패 시**: `--dir` 옵션으로 폴더 직접 지정 후 재시도
5. **TIL 기록**: 핵심개념 수 + 액션아이템 + Notion URL 포함

## 관련 개념
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- 260515_openclaw
- til-patterns-2026-05
- [claude-code](/tools/claude-code.md) — `/meeting`, `/meeting_end` 슬래시 커맨드 실행 환경
- [whisper-ecosystem](/tools/whisper-ecosystem.md) — audio_scribe.py의 Whisper turbo STT 엔진
- [ai-pm-role](/concepts/ai-pm-role.md) — 회의 자동화가 PM 에이전시를 강화하는 연결점
- [agent-build-harness](/insights/agent-build-harness.md) — LaunchAgent 상시 실행 + 캘린더 트리거 하네스 패턴과 동형
