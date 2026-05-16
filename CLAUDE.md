# LLM Wiki — Claude Code 운영 가이드

## 역할 정의

Claude는 이 wiki의 **컴파일러**다. 사용자는 raw 데이터를 공급하고 질문하며, Claude는 `schema/`의 규칙에 따라 `wiki/`를 생성·갱신한다.

```
사용자: raw 데이터 공급 + 질문
Claude: wiki/ 작성 및 유지 (schema/ 규칙 준수)
```

## 디렉토리 구조

```
~/Documents/3_Code/Vibe/Project/260516_llm_brain/
├── raw/          원본 소스 (불변 — Claude가 수정하지 않는다)
│   ├── til/          OpenClaw TIL 미러
│   ├── meetings/     OpenClaw 회의록 미러
│   ├── newsletters/  OpenClaw 뉴스레터 미러
│   ├── context/      OpenClaw 비즈니스 컨텍스트 미러
│   ├── blog/         habix blog 콘텐츠 미러
│   ├── clippings/    /ingest URL 수동 스크랩
│   └── notes/        /ingest "텍스트" 수동 노트
├── wiki/         LLM이 컴파일한 정제 지식
│   ├── concepts/     AI·기술 개념
│   ├── tools/        도구·프레임워크
│   ├── people/       인물
│   ├── projects/     프로젝트 인사이트
│   ├── business/     시장·경쟁사·전략
│   ├── lecture/      강의 지식
│   └── insights/     TIL 정제본·반복 패턴
├── schema/       운영 규칙 (이 파일들을 읽고 작동)
├── index.md      전체 wiki 목차
├── log.md        실행 이력
└── scripts/      자동화 스크립트
```

## 핵심 가드레일 (절대 위반 금지)

1. **raw 없이 wiki 수정 금지**: `raw/`에 출처 파일 없이 `wiki/` 페이지를 신규 생성하거나 사실 관계를 수정하지 않는다.
2. **query 중 wiki 편집 금지**: 사용자 질문에 답하는 도중에 `wiki/` 파일을 수정하지 않는다.
3. **외부 지식으로 wiki 채우기 금지**: Claude의 학습 데이터로만 wiki 페이지를 작성하지 않는다. 반드시 `raw/` 파일에 근거가 있어야 한다.
4. **raw/ 파일 수정 금지**: `raw/`는 불변 소스다. Claude는 읽기만 한다.

## 명령어

### ingest
새로운 `raw/` 파일을 `wiki/`로 컴파일한다.

```
사용자: "ingest 해줘"
또는: "/ingest https://example.com"
또는: "/ingest ~/Downloads/paper.pdf --resonance high"
또는: "/ingest '텍스트' --resonance medium"
```

실행 절차:
1. `scripts/ingest.py`로 미처리 파일 목록 확인 (중복 검사 포함)
2. `schema/ingest.md` 규칙 로드
3. 각 raw 파일을 읽고 관련 wiki/ 페이지 생성 또는 갱신
4. `[[wikilink]]` 형식으로 관련 페이지 cross-link
5. `index.md` 갱신 (distill_level: 0, access_count: 0 frontmatter 포함)
6. `log.md`에 작업 이력 기록

### curate
wiki 전체를 감사·압축·수명 관리한다.

```
사용자: "curate 해줘"
또는: "curate --audit"
또는: "curate --distill"    ← distill_level 점진적 압축
또는: "curate --lifecycle"
또는: "curate --graph"      ← 링크 그래프 분석 (NEW)
또는: "curate --all"        ← 전체 (graph 포함)
```

- `--distill`: wiki/distill_queue.md를 읽고 distill_level 기준으로 페이지 압축. 압축 후 frontmatter 갱신.
- `--graph`: wiki/graph_report.md를 읽고 허브 페이지 distill 우선 처리 + 합성 후보 제안.
- `schema/curate.md` 참조.

### query
wiki를 바탕으로 질문에 답한다.

```
사용자: "RAG에 대해 알려줘"
사용자: "habix 경쟁사 현황은?"
```

실행 절차:
1. `index.md`에서 관련 wiki 페이지 식별
2. 해당 페이지들만 로드
3. **wiki 내용 기반으로만** 답변 (wiki에 없으면 "raw 데이터가 필요합니다" 응답)
4. `scripts/curate.py --record-access {slug}`로 접근 기록 (distill 우선순위에 반영)

### express
wiki 페이지를 창작물로 출력한다. (NEW)

```
사용자: "express blog '에이전트 설계 패턴에 대해'"
또는: "express lecture 'context-first' --slides 3"
또는: "express summary --week"
또는: "express summary --month"
또는: "express report 'habix 경쟁사'"
```

실행 절차:
1. `scripts/express.py`로 관련 wiki 페이지 수집 및 컨텍스트 준비
2. 출력 형식에 맞는 구조로 창작물 생성
3. `express/{type}/YYYY-MM-DD-{slug}.md` 저장
4. blog 타입: `raw/blog/`에도 복사 → 다음 ingest에서 wiki 피드백 루프

## wiki 페이지 형식

```markdown
---
title: 페이지 제목
type: concept | tool | person | project | business | lecture | insight
domain: AI/LLM | teaching | habix | tools | personal
tags: [태그1, 태그2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/파일경로1, raw/파일경로2]
---

# 제목

## 핵심 요약
(2-3줄 핵심 정의)

## 상세 내용
...

## 관련 개념
- [[연관페이지1]]
- [[연관페이지2]]
```

## 파일 명명 규칙

- 소문자, 하이픈 구분: `retrieval-augmented-generation.md`
- 한국어 개념은 영문 slug: `agent-memory-pattern.md`
- 인물: `firstname-lastname.md`
- **프로젝트**: `YYMMDD_project_name.md` — 예) `260515_llm_wiki.md`
  - 날짜는 wiki 페이지 최초 생성일 기준 (raw 소스 날짜 아님)
  - 서브폴더도 동일 규칙: `260515_llm_wiki/prd.md`
  - 하이픈 대신 언더스코어 사용

## Wikilink 규칙

- 형식: `[[페이지명]]` (확장자 없이)
- 페이지가 존재하지 않으면 link만 추가하고 ghost 목록에 등록
- 같은 페이지 내 중복 link 금지

## index.md 갱신 규칙

ingest 후 반드시 `index.md`를 갱신한다. 형식:

```
## concepts/ (N개)
- [[page-name]] — 한 줄 설명
```

전체가 단일 컨텍스트 윈도우 안에 들어오도록 유지한다 (목표: 4000 토큰 이하).
