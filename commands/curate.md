---
description: wiki 품질 관리 — 감사(audit)·압축(distill)·수명 관리(lifecycle)
---

llm-brain의 curate 커맨드입니다. `$ARGUMENTS`에 따라 아래를 실행하세요.

## 인자 파싱

- `--distill` → distill 모드
- `--lifecycle` → lifecycle 모드
- `--audit` → audit 모드
- `--all` 또는 인자 없음 → 전체 실행 (audit + distill + lifecycle)
- `--purge` → archive 후보 실제 이동

> 그래프 탐색은 `/ingest` (delta canvas)와 `/query` (neighborhood canvas)가 담당합니다.

## Step 1: curate 스크립트 실행

```bash
cd "$(git rev-parse --show-toplevel)"  # llm-brain 레포 루트
uv run python scripts/curate.py $ARGUMENTS
```

실행 결과로 `wiki/curate_report.md`, `wiki/distill_queue.md`가 생성됩니다.

## Step 2: distill 실행 (--distill 또는 --all 일 때)

`wiki/distill_queue.md`의 **긴급 후보**(access ≥ 10, distill_level < 3)를 순서대로 압축합니다:

각 대상 페이지에 대해:
1. 현재 페이지 내용 읽기
2. `distill_level`에 따라 압축:
   - level 0 → 1: 원문에서 핵심 단락만 추출 (50% 축약)
   - level 1 → 2: 핵심 개념과 관계만 남기기 (30% 이하)
   - level 2 → 3: 한 문장 핵심 요약 추가
3. frontmatter의 `distill_level` 값 +1, `last_distilled` 오늘 날짜로 갱신

## Step 3: 결과 요약 출력

실행한 모드별 결과를 한국어로 요약:
- orphan 페이지 수
- stale wikilink 수
- distill 큐 크기
- lifecycle 후보 수
