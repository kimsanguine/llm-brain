---
description: raw/ 소스 ingest → wiki/ 컴파일 (URL·파일·텍스트 지원)
---

llm-brain의 ingest 커맨드입니다. 아래 절차를 순서대로 실행하세요.

## 인자 파싱

`$ARGUMENTS`를 파싱해 모드를 결정합니다:

- `https://...` 또는 `http://...` 로 시작 → URL 모드
- `--file <경로>` 포함 → 파일 모드
- `--note "<텍스트>"` 포함 → 노트 모드
- `--resonance high|medium|low` 옵션이 있으면 해당 레벨 사용
- `--priority-only` → resonance: high 미처리 파일만 처리
- 인자 없음 → 미처리 파일 목록만 확인

## Step 1: 스크립트 실행

인자에 따라 아래 중 해당하는 명령 실행:

```bash
# URL 수집
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python scripts/ingest.py --url <URL> [--resonance <level>]

# 파일 추가
uv run python scripts/ingest.py --file <경로> [--resonance <level>]

# 텍스트 노트
uv run python scripts/ingest.py --note "<텍스트>" [--resonance <level>]

# 미처리 목록 확인 (인자 없음)
uv run python scripts/ingest.py [--priority-only]
```

exit code 0 = 처리할 파일 없음, exit code 1 = 미처리 파일 있음.

## Step 2: wiki 컴파일

스크립트 출력에서 미처리 파일 목록을 확인합니다.
미처리 파일이 있으면 `schema/ingest.md` 규칙에 따라 각 파일을 wiki 페이지로 컴파일합니다:

1. 각 raw 파일 내용 읽기
2. `schema/domains.yaml` 기준 도메인 분류
3. `index.md`에서 관련 기존 페이지 확인
   - 기존 페이지 있음 → 갱신 (sources 추가, 내용 병합)
   - 없음 → 신규 생성 (wiki frontmatter 포함)
4. wikilink 교차 연결
5. `index.md` 갱신

## Step 3: 완료 표시

wiki 컴파일 완료 후:
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python scripts/ingest.py --mark-done
```

## 가드레일 (절대 위반 금지)

- `raw/` 파일 수정 금지 (읽기 전용)
- `raw/` 근거 없이 wiki 사실 수정 금지
- Claude 학습 데이터만으로 wiki 작성 금지
