---
type: project
title: LLM Wiki — 운영 가이드
description: claude-code CLI(claude -p)를 실행 엔진으로 하는 명령어 체계.
tags:
- operations
- llm-wiki
- runbook
- personal-tool
timestamp: '2026-05-15'
x-llmbrain-domain:
- tools
- habix
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM Wiki — 운영 가이드

## 오퍼레이션 명령어

[claude-code](/tools/claude-code.md) CLI(`claude -p`)를 실행 엔진으로 하는 명령어 체계. claude-code-workflow 패턴을 따라 비대화형 자동화와 대화형 온디맨드 실행을 구분한다.

| 명령어 | 트리거 | 역할 |
|---|---|---|
| `sync` | launchd 매일 07:00 | OpenClaw/habix blog → raw/ 미러링 |
| `ingest` | sync 후 자동 + 온디맨드 | raw/ → wiki/ 컴파일 |
| `/ingest URL` | [claude-code](/tools/claude-code.md)에서 직접 | URL 스크랩 + 즉시 ingest |
| `curate --all` | 매주 월요일 | 감사 + 압축 + lifecycle 후보 |
| `curate --purge` | 사용자 확인 후 수동 | archive 후보 실제 이동 |
| `query` | 언제든지 | wiki 기반 질문 답변 |

---

## sync

```bash
cd ~/llm-wiki
uv run python scripts/sync_raw.py
```

- `schema/sources.yaml`의 소스 경로에서 파일 복사
- `.sync_state.json`으로 delta 감지 (마지막 동기화 이후 변경분만)
- 실행 후 새 파일이 있으면 `ingest` 필요

---

## ingest

**온디맨드 (Claude Code 대화에서)**
```
ingest 해줘
```

**URL 스크랩**
```
/ingest https://example.com/article
```

**PDF 스크랩**
```
/ingest ~/Downloads/paper.pdf
```

**자동 (launchd)**
```bash
# run_daily.sh가 자동 실행
python scripts/ingest.py        # 새 파일 감지
# 새 파일 있으면 claude -p로 ingest 실행
python scripts/ingest.py --mark-done  # 처리 완료 표시
```

**수동 강제 실행**
```bash
uv run python scripts/ingest.py  # exit 0 = 없음, exit 1 = 있음
```

---

## curate

**전체 실행**
```
curate 해줘
```

**개별 실행**
```
curate --audit      # orphan/stale 링크만
curate --distill    # insights 압축만
curate --lifecycle  # archive 후보 목록만
```

**archive 실행 (확인 후)**
```bash
# wiki/curate_report.md 확인 후
uv run python scripts/curate.py --purge
```

---

## launchd 스케줄

```
~/Library/LaunchAgents/ai.habix.llm-wiki.plist
매일 07:00 KST 실행
```

**상태 확인**
```bash
launchctl list | grep llm-wiki
```

**재로드**
```bash
launchctl unload ~/Library/LaunchAgents/ai.habix.llm-wiki.plist
launchctl load ~/Library/LaunchAgents/ai.habix.llm-wiki.plist
```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| ingest 후 wiki 페이지 없음 | `.ingest_state.json`이 이미 처리됨으로 표시 | `python scripts/ingest.py` 실행해 pending 확인 |
| sync가 파일 누락 | exclude_tags에 걸린 파일 | raw 파일 frontmatter 태그 확인 |
| curate report 비어 있음 | wiki 페이지 부족 | ingest 먼저 실행 |
| launchd 미실행 | plist 언로드됨 | `launchctl load` 재실행 |

---

## 도메인 분류 기준

| raw 소스 | 우선 도메인 | 예시 |
|---|---|---|
| raw/til/ | insights/ | TIL 패턴 압축본 |
| raw/meetings/ | projects/ 또는 business/ | 회의 결정사항 |
| raw/newsletters/ | concepts/ 또는 tools/ | AI 개념, 새 도구 |
| raw/context/ | business/ 또는 projects/ | 비즈니스 컨텍스트 |
| raw/blog/ | concepts/ 또는 tools/ | 기술 블로그 정제 |
| raw/clippings/ | 내용에 따라 | URL 스크랩 |

---

## 관련 문서
- [prd](/projects/260515_llm_wiki/prd.md)
- [architecture](/projects/260515_llm_wiki/architecture.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)

## 외부 카테고리 연결
- [claude-code](/tools/claude-code.md) — 실행 엔진, `claude -p` 비대화형 호출 패턴
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — 에이전트 자동화 운영 설계 참조
- [agent-build-harness](/insights/agent-build-harness.md) — launchd + dangerously-skip-permissions 자율 실행 하네스 패턴
- til-patterns-2026-05 — 운영 중 학습한 패턴 (ingest 실패 케이스, curate 최적화)
- habix-profile — 운영자 정체성, habix 서비스와의 연동 컨텍스트
- claude-code-workflow — 비대화형 CLI 워크플로우 설계 원칙
