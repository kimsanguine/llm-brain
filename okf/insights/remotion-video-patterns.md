---
type: insight
title: Remotion 영상 제작 패턴
description: Remotion 기반 영상 제작은 remotion-best-practices 스킬 우선 적용.
tags:
- remotion
- video-pipeline
- ffmpeg
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

# Remotion 영상 제작 패턴

## 핵심 원칙

Remotion 기반 영상 제작은 `remotion-best-practices` 스킬 우선 적용. 프로젝트는 항상 신규 폴더로 격리, 기존 폴더 overwrite 금지.

## 발견된 패턴

### Composition ID 명명 규칙 (2026-03-03, 2026-03-04)
- Remotion composition ID에 언더스코어(`_`)를 쓰면 렌더 오류 발생
- 하이픈(`-`) 또는 영숫자 조합만 허용
- 예: `BarLineChart` (O), `Bar_Line_Chart` (X)

### 인물 합성 품질 패턴 (2026-03-03, 2026-03-04)
- 코드로 인물을 직접 그리는 방식보다 실제 컷아웃 이미지(`<Img>`)를 사용하고 모션만 제어
- 결과물 품질 차이 명확

### BGM 페이드 제어 (2026-03-03, 2026-03-04)
- `@remotion/media`의 `Audio` volume callback으로 프레임 단위 제어
- 1초 페이드인 / 2초 페이드아웃 / 40% 볼륨 패턴이 안정적

### 씬 구조화 패턴 (2026-03-03, 2026-03-04)
- `AppWindow` 공통 래퍼 + `Series` 씬 분할 조합
- UI 일관성과 유지보수성 모두 향상

### 렌더 파이프라인 분리 (2026-03-03, 2026-03-04)
- `npm run build` (타입 체크) → `npm run render` (mp4) → `ffmpeg` (gif)
- 단계 분리로 문제 원인 추적이 쉬워짐

### 오디오 파일 경로 관리 (2026-03-03, 2026-03-04)
- 오디오 파일은 `public/` 디렉토리에 배치
- `--music` 옵션으로 오디오 포함 렌더

### 요청 변경 대응 원칙 (2026-03-04)
- 툴 호출이 중단되면 동일 접근 반복 대신 즉시 사용자 의도에 맞춰 경로/방식 전환

## 적용 방법

1. 신규 프로젝트 시작 시 `remotion-best-practices` 스킬 로드
2. Composition ID: 하이픈 또는 영숫자 조합으로 명명
3. 인물 씬: 코드 드로잉 대신 `<Img>` + 모션 제어 방식 선택
4. 오디오: `public/` 에 파일 배치 후 `Audio` volume callback으로 페이드 처리
5. 렌더: build → render → ffmpeg 순서로 단계별 실행

## 관련 개념
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- til-patterns-2026-05
- [pptx-automation-patterns](/insights/pptx-automation-patterns.md)
- [youtube-dubbing-patterns](/insights/youtube-dubbing-patterns.md)
