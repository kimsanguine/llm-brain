# llm-brain — Claude Code 운영 지침

Claude는 이 시스템의 **컴파일러**다. `raw/` 소스를 읽어 `wiki/`를 생성·갱신하고, 사용자 질문에 wiki 기반으로 답한다.

## 가드레일 (절대 위반 금지)

1. `raw/` 출처 없이 `wiki/` 신규 생성·사실 수정 금지
2. query 응답 중 `wiki/` 편집 금지
3. 학습 데이터만으로 `wiki/` 작성 금지 — 반드시 `raw/` 근거 필요
4. `raw/` 파일 수정 금지 — 읽기 전용

## 명령어

### ingest
```
"ingest 해줘"
"/ingest https://url [--resonance high|medium|low]"
"/ingest ~/path/to/file.pdf [--resonance high]"
"/ingest '텍스트 내용' [--resonance medium]"
```
`scripts/ingest.py` 실행 → `schema/ingest.md` 규칙 적용 → `wiki/` 생성·갱신 → `index.md` 업데이트

### curate
```
"curate --distill"     # distill_level 점진 압축
"curate --graph"       # wikilink 그래프 분석, 허브 감지
"curate --lifecycle"   # TTL 초과 페이지 archive 후보
"curate --all"         # 전체 실행
```
`scripts/curate.py` 실행 → `schema/curate.md` 규칙 적용

### query
```
"[질문]에 대해 알려줘"
```
`index.md` 검색 → 관련 `wiki/` 페이지 로드 → wiki 기반 답변
wiki에 없으면: "raw 데이터가 필요합니다" 응답
접근한 페이지 `access_count` 갱신

### express
```
"express blog '[주제]'"
"express lecture '[주제]' --slides N"
"express summary --week"
"express report '[주제]'"
```
`scripts/express.py` 실행 → `express/{type}/YYYY-MM-DD-{slug}.md` 저장
blog: `raw/blog/`에도 복사 (ingest 피드백 루프)

### wiki-web (HTML 검색 페이지)
```
uv run python -m wiki_app
# → http://localhost:8000
```
로컬 HTML 검색·페이지뷰 인터페이스. CLI `/query`의 시각화 버전.

- **검색 알고리즘**: 제목+desc+tags+page_title 점수 매칭 (B). 결과 < 3개 시 본문 grep 자동 확장 (C). 한국어/영문 모두 작동.
- **AI 답변 토글**: `claude -p` CLI 라이브 연결 (SSE 스트리밍 `/api/ai-answer/stream` 포함). CLI 부재 시 `status: unavailable` fallback.
- **백엔드**: `wiki_app/` (FastAPI · uv) — 6 endpoints (`/api/index`, `/api/search`, `/api/page/{slug}`, `/api/page/{slug}/graph`, `/api/ai-answer`, `/api/ai-answer/stream`)
- **프론트엔드**: `wiki_app/static/` (vanilla JS + Pretendard)
- **테스트**: `tests/test_wiki_app_*.py` (5 modules, 26 tests)
- **운영 가드레일**: 페이지뷰 시 wiki frontmatter `access_count` 자동 +1 (CLI query와 동등)
- **설계 문서**: `docs/superpowers/specs/2026-05-22-wiki-search-html-mvp-design.md`

## 파일 명명

- wiki 페이지: `소문자-하이픈.md` (한국어 개념도 영문 slug)
- 프로젝트: `YYMMDD_project_name/` (언더스코어)
- wikilink: `[[페이지명]]` (확장자 없이)

## wiki frontmatter

```yaml
title: ...
type: concept|tool|person|project|business|lecture|insight
tags: [...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/파일경로]
distill_level: 0     # 0=원문 1=요약 2=핵심 3=한줄
access_count: 0
```

> 상세 스펙: `SPEC.md` / 사용 가이드: `README.md`
