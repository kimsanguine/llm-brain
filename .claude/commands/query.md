---
description: wiki 기반 질문 답변 (wiki에 없으면 raw 필요 안내)
---

llm-brain의 query 커맨드입니다. 질문: **$ARGUMENTS**

아래 절차로 wiki 기반 답변을 제공하세요.

## Step 1: index.md 검색

`index.md`를 읽고 질문과 관련된 wiki 페이지 목록을 식별합니다.
키워드 매칭으로 관련도 높은 페이지 최대 5개를 선정합니다.

## Step 2: wiki 페이지 로드

선정된 wiki 페이지들을 읽습니다.
관련 페이지가 없으면:
> "이 주제에 대한 wiki 데이터가 없습니다. `/ingest` 로 관련 소스를 먼저 추가해주세요."
라고 응답하고 종료합니다.

## Step 3: wiki 기반 답변

읽은 wiki 페이지 내용만을 근거로 답변합니다.

**중요 원칙**:
- wiki 페이지에 없는 내용은 "wiki에 해당 정보가 없습니다"라고 명시
- Claude 학습 데이터로 wiki 내용을 보완하지 않음
- 답변 마지막에 참조한 wiki 페이지 목록을 `[[페이지명]]` 형식으로 표시

## Step 4: access_count 갱신

답변에 사용한 각 페이지의 slug에 대해:
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python scripts/curate.py --record-access <페이지_slug>
```
