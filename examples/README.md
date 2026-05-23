# Examples — seed-wiki

llm-brain을 fresh clone한 사용자가 **즉시 wiki_app 데모를 보기 위한** 5페이지 sample wiki.

## 사용법

### Option A — 데모만 보고 자기 wiki 시작 (권장)

```bash
# seed-wiki를 작업 디렉토리로 복사
cp -r examples/seed-wiki/* ./
mv examples/seed-wiki/index.md ./index.md

# wiki_app 실행
uv run python -m wiki_app
# → http://localhost:8000 에서 5개 sample 페이지 검색 가능
```

이후 자신의 raw 소스를 `raw/`에 추가하고 ingest → wiki/ 구축.

### Option B — 자기 wiki만 사용 (seed 건너뛰기)

`examples/`를 무시하고 README의 빠른 시작 가이드만 따르세요.

## seed-wiki 구성

- `concepts/llm-wiki-pattern.md` — Karpathy 패턴
- `concepts/second-brain-code.md` — Tiago Forte CODE 프레임워크
- `concepts/distill-progressive.md` — Progressive Summarization
- `tools/claude-code.md` — Claude Code CLI
- `tools/obsidian.md` — Obsidian

상호 wikilink 13개로 연결돼 있어, wiki_app의 검색·페이지뷰·wikilink 클릭 모두 즉시 작동합니다.

## CI 영향

이 seed 데이터는 `tests/conftest.py`의 `_HAS_USER_WIKI` fallback에도 사용됩니다. GitHub Actions가 `examples/seed-wiki/`를 wiki 데이터로 활용해 21개 wiki-dependent test를 skip 없이 실행할 수 있습니다 (CI workflow에 복사 step 추가 후).
