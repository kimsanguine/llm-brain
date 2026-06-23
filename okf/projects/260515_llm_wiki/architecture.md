---
type: project
title: LLM Wiki — 아키텍처
description: karpathy의 원본 설계에서 4가지 축을 확장한다.
tags:
- architecture
- llm-wiki
- system-design
timestamp: '2026-05-15'
x-llmbrain-domain:
- tools
- habix
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM Wiki — 아키텍처

## 계층 구조

```
[소스]                             [raw/]           [wiki/]
OpenClaw TIL (48+)    ──sync──▶  raw/til/     ──▶  insights/
OpenClaw meetings     ──sync──▶  raw/meetings/ ──▶  (요약 반영)
OpenClaw newsletters  ──sync──▶  raw/newsletters/ ──▶ concepts/ or tools/
OpenClaw context      ──sync──▶  raw/context/  ──▶  business/
habix blog            ──sync──▶  raw/blog/     ──▶  projects/ or concepts/
/ingest URL           ──────▶   raw/clippings/ ──▶  concepts/ or tools/
/ingest "텍스트"       ──────▶   raw/notes/    ──▶  (적합 도메인)
```

## Karpathy 원본 대비 확장

[karpathy](/people/karpathy.md)의 원본 설계에서 4가지 축을 확장한다. LLM을 컴파일러로 쓰는 아이디어는 [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md) 관점에서 "LLM-as-tool" 패턴의 실용적 구현이기도 하다.

| 항목 | Karpathy 원본 | 이 시스템 |
|---|---|---|
| 입력 | 수동 raw 파일 추가 | OpenClaw vault 자동 미러링 |
| 오퍼레이션 | ingest / query / lint | sync / ingest / curate |
| LLM 호출 | API 직접 | [claude-code](/tools/claude-code.md) CLI (`claude -p`) |
| 시각화 | 없음 | Obsidian Graph View ([steph-ango](/people/steph-ango.md) 설계) |

## 파일 시스템

```
~/llm-wiki/
├── raw/                 원본 소스 (불변 — Claude가 수정하지 않음)
│   ├── til/             OpenClaw TIL 미러
│   ├── meetings/        OpenClaw 회의록 미러
│   ├── newsletters/     OpenClaw 뉴스레터 미러
│   ├── context/         OpenClaw 비즈니스 컨텍스트 미러
│   ├── blog/            habix blog 포스트 미러
│   ├── clippings/       /ingest URL 스크랩
│   └── notes/           /ingest 텍스트 노트
├── wiki/                LLM이 컴파일한 정제 지식
│   ├── concepts/        AI·기술 개념
│   ├── tools/           도구·프레임워크
│   ├── people/          인물
│   ├── projects/        프로젝트 인사이트
│   │   └── llm-wiki/    이 프로젝트 개발 문서
│   ├── business/        시장·경쟁사·전략
│   ├── lecture/         강의 지식
│   └── insights/        TIL 정제본·반복 패턴
├── schema/              운영 규칙
│   ├── sources.yaml     소스 경로 + TTL 설정
│   ├── ingest.md        ingest 상세 규칙
│   ├── curate.md        curate 상세 규칙
│   └── domains.yaml     도메인 분류 기준
├── scripts/
│   ├── sync_raw.py      소스 → raw/ 미러링
│   ├── ingest.py        새 파일 감지 + URL 스크랩
│   ├── curate.py        audit + lifecycle (Python)
│   └── run_daily.sh     launchd 진입점
├── CLAUDE.md            Claude Code 운영 가이드 (자동 로드)
├── index.md             전체 wiki 목차
└── log.md               실행 이력
```

## 스크립트 설계

### sync_raw.py
- `schema/sources.yaml`에서 소스 경로 읽기
- `.sync_state.json`으로 마지막 동기화 시간 추적 (delta detection)
- `exclude_tags` frontmatter로 private 파일 필터링
- API 호출 없음 — 순수 파일 복사

### ingest.py
- `.ingest_state.json`으로 처리된 파일 추적
- 미처리 파일 있으면 exit code 1 → `run_daily.sh`이 `claude -p` 호출
- `--mark-done` 플래그로 처리 완료 표시
- `/ingest URL` 시: httpx 스크랩 → markdownify 변환 → raw/clippings/ 저장

### curate.py
- `run_audit()`: wikilink 그래프 분석, orphan/stale 링크 탐지
- `run_lifecycle()`: TTL 기반 archive 후보 목록 생성 (삭제 안 함)
- `run_distill()`: insight 후보 목록만 반환, 실제 압축은 Claude Code CLI 위임
- `do_purge()`: `--purge` 명시 시에만 archive/ 이동 실행

### run_daily.sh
```bash
# 07:00 KST launchd 실행
python scripts/sync_raw.py --quiet
python scripts/ingest.py
if [ $? -eq 1 ]; then
    claude --dangerously-skip-permissions -p "ingest 해줘"
    python scripts/ingest.py --mark-done
fi
# 매주 월요일
if [ $(date +%u) -eq 1 ]; then
    python scripts/curate.py --audit --lifecycle
    claude --dangerously-skip-permissions -p "curate --distill 해줘"
fi
```

## TTL 정책

| 도메인 | TTL | 이유 |
|---|---|---|
| concepts / tools / people / projects / business / lecture | 무기한 | 영속 지식 |
| insights | 365일 | TIL 정제본, 1년 후 검토 |
| til / meetings / newsletters (raw/) | 60–180일 | 시효성 소스 |

## 핵심 가드레일

1. **raw 없이 wiki 수정 금지** — hallucination 방지
2. **query 중 wiki 편집 금지** — 일관성 보장
3. **외부 지식으로 wiki 채우기 금지** — raw 근거 필수
4. **raw/ 파일 수정 금지** — 불변 소스

가드레일 설계는 [claude-code-agent-system](/tools/claude-code-agent-system.md)의 scope 제한 패턴을 참조. [agent-build-harness](/insights/agent-build-harness.md)에서 안전한 자율 실행 설계 원칙을 차용.

## 관련 문서
- [prd](/projects/260515_llm_wiki/prd.md)
- [operations](/projects/260515_llm_wiki/operations.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)

## 외부 카테고리 연결
- [karpathy](/people/karpathy.md) — raw→wiki 2계층 아이디어 원조, LLM-as-compiler 패턴
- [steph-ango](/people/steph-ango.md) — Obsidian Graph View 설계자 (CEO), wikilink 그래프 시각화 근거
- [claude-code](/tools/claude-code.md) — CLI 실행 엔진, `claude -p` 비대화형 호출 패턴
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — 에이전트 scope 제한 + 가드레일 설계 패턴 참조
- [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md) — LLM-as-tool 아키텍처 패러다임 맥락
- [agent-build-harness](/insights/agent-build-harness.md) — 자율 실행 안전 설계, dangerously-skip-permissions 패턴
