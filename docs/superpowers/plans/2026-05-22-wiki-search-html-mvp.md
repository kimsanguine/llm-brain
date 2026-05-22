# Wiki Search HTML MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** llm-brain의 wiki 데이터(50 페이지)를 로컬 HTTP 서버에서 검색·페이지뷰가 가능한 HTML 페이지로 제공한다. AI 답변 endpoint는 1차에서 stub만 두고 UI는 풀버전으로 만든다.

**Architecture:** Python FastAPI 백엔드(uv 환경, `wiki_app/` 신규 패키지) + vanilla JS frontend(static 파일, framework 없음). 백엔드는 기존 `wiki/`, `scripts/curate.py:record_access`를 재사용. 검색은 점진적 확장(제목+desc+tags → 결과 < 3개면 본문 grep으로 자동 확장).

**Tech Stack:** Python 3.13 · FastAPI · uvicorn · markdown-it-py · python-frontmatter (기존) · vanilla JS · Pretendard CDN

**Spec:** `docs/superpowers/specs/2026-05-22-wiki-search-html-mvp-design.md`

---

## File Structure

신규/수정 파일 + 책임:

```
260516_llm_brain/
├── wiki_app/                          # 신규 패키지
│   ├── __init__.py                    # 빈 파일
│   ├── __main__.py                    # uvicorn entry point
│   ├── api.py                         # FastAPI app + 4 endpoints
│   ├── search.py                      # index 빌드 + B/C 알고리즘
│   ├── pages.py                       # 페이지 로더 (frontmatter + body)
│   ├── render.py                      # markdown-it + wikilink 변환
│   ├── access.py                      # scripts/curate.record_access wrapper
│   └── static/
│       ├── index.html                 # HTML 골격
│       ├── styles.css                 # Pretendard + 디자인 톤
│       └── app.js                     # 상태관리·fetch·검색·페이지뷰·AI 토글
├── tests/
│   ├── test_wiki_app_pages.py         # Task 1 테스트
│   ├── test_wiki_app_render.py        # Task 2 테스트
│   ├── test_wiki_app_search.py        # Task 3,4 테스트
│   ├── test_wiki_app_access.py        # Task 5 테스트
│   └── test_wiki_app_api.py           # Task 6 테스트 (FastAPI TestClient)
├── pyproject.toml                     # 의존성 추가
└── uv.lock                            # uv add로 자동 갱신
```

각 모듈 책임:
- **pages.py**: `load_page(slug) → {slug, category, frontmatter, body_md, inbound, outbound}` 단일 책임
- **render.py**: `render(body_md) → html` — wikilink `[[slug]]` → `<a data-link="slug">` 정규식 후처리
- **search.py**: `Index` 클래스 — 서버 시작 시 빌드, `search(q) → results` 메서드
- **access.py**: `track(slug)` — scripts/curate.record_access wrapper
- **api.py**: FastAPI routes만, 로직은 위 모듈에 위임
- **frontend**: 단일 SPA, 백엔드 fetch로 모든 데이터 수신

---

## Task 0: 의존성 추가 + 패키지 스캐폴딩

**Files:**
- Modify: `pyproject.toml` (uv add 자동)
- Create: `wiki_app/__init__.py`
- Create: `wiki_app/static/.gitkeep`

- [ ] **Step 1: 의존성 추가**

Run:
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv add fastapi 'uvicorn[standard]' markdown-it-py httpx
```

Expected output: `Resolved N packages`, pyproject.toml의 `dependencies` 리스트에 4개 추가됨.
(httpx는 이미 있으면 skip — TestClient 사용 위해 필요)

- [ ] **Step 2: requirements.txt 동기화**

Run:
```bash
uv export --frozen --no-dev --no-emit-project -o requirements.txt
```

Expected: requirements.txt 갱신, CLAUDE.md의 source-of-truth 규칙 충족.

- [ ] **Step 3: 패키지 디렉토리 생성**

Run:
```bash
mkdir -p wiki_app/static
touch wiki_app/__init__.py wiki_app/static/.gitkeep
```

Expected: 디렉토리·빈 파일 생성 확인.
```bash
ls wiki_app/
# __init__.py  static/
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock requirements.txt wiki_app/
git commit -m "feat(wiki_app): scaffold package + add FastAPI deps"
```

---

## Task 1: pages.py — 페이지 로더

**Files:**
- Create: `wiki_app/pages.py`
- Create: `tests/test_wiki_app_pages.py`

페이지 slug를 받아 frontmatter + body + graph 메타데이터를 dict로 반환한다.

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_wiki_app_pages.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from wiki_app.pages import load_page, find_page_path, PageNotFound


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


def test_load_known_page_returns_frontmatter_and_body():
    page = load_page("habix-profile", wiki_root=WIKI_ROOT)
    assert page["slug"] == "habix-profile"
    assert page["category"] == "business"
    assert "habix" in page["frontmatter"]["tags"]
    assert page["body_md"].startswith("# habix 비즈니스 프로파일")


def test_load_page_includes_graph_metadata():
    page = load_page("habix-profile", wiki_root=WIKI_ROOT)
    assert "inbound" in page
    assert "outbound" in page
    assert isinstance(page["inbound"], int)


def test_load_missing_page_raises():
    with pytest.raises(PageNotFound):
        load_page("nonexistent-slug", wiki_root=WIKI_ROOT)


def test_find_page_path_searches_all_categories():
    p = find_page_path("habix-profile", wiki_root=WIKI_ROOT)
    assert p.name == "habix-profile.md"
    assert p.parent.name == "business"
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_pages.py -v
```

Expected: 4 FAIL — `ModuleNotFoundError: No module named 'wiki_app.pages'`

- [ ] **Step 3: pages.py 구현**

Create `wiki_app/pages.py`:
```python
"""페이지 로더 — frontmatter + 본문 + graph 메타데이터."""
from __future__ import annotations

import json
from pathlib import Path

import frontmatter


class PageNotFound(Exception):
    pass


_CATEGORIES = ("concepts", "tools", "people", "projects", "business", "lecture", "insights")


def find_page_path(slug: str, wiki_root: Path) -> Path:
    """slug에 해당하는 마크다운 파일을 카테고리 폴더에서 찾는다."""
    # 서브폴더 케이스 (예: 260515_llm_wiki/prd)
    if "/" in slug:
        for cat in _CATEGORIES:
            candidate = wiki_root / cat / f"{slug}.md"
            if candidate.exists():
                return candidate
    for cat in _CATEGORIES:
        candidate = wiki_root / cat / f"{slug}.md"
        if candidate.exists():
            return candidate
    raise PageNotFound(f"slug not found: {slug}")


def _load_graph(wiki_root: Path) -> dict:
    """graph.json을 로드하고 slug → degree 매핑을 만든다."""
    graph_path = wiki_root / "graph.json"
    if not graph_path.exists():
        return {}
    graph = json.loads(graph_path.read_text())
    return {n["id"]: n for n in graph["nodes"] if n.get("kind") == "page"}


def load_page(slug: str, wiki_root: Path) -> dict:
    """페이지 데이터를 dict로 반환한다."""
    path = find_page_path(slug, wiki_root)
    post = frontmatter.load(path)
    graph_nodes = _load_graph(wiki_root)
    node = graph_nodes.get(slug, {})
    return {
        "slug": slug,
        "category": path.parent.name,
        "frontmatter": post.metadata,
        "body_md": post.content,
        "inbound": node.get("inbound", 0),
        "outbound": node.get("outbound", 0),
    }
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_pages.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add wiki_app/pages.py tests/test_wiki_app_pages.py
git commit -m "feat(wiki_app): pages.load_page — frontmatter + body + graph metadata"
```

---

## Task 2: render.py — 마크다운 + wikilink 변환

**Files:**
- Create: `wiki_app/render.py`
- Create: `tests/test_wiki_app_render.py`

마크다운 본문을 HTML로 변환하면서 `[[slug]]` 패턴을 SPA에서 클릭 가능한 링크로 후처리한다.

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_wiki_app_render.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wiki_app.render import render_markdown


def test_basic_markdown_to_html():
    html = render_markdown("# 제목\n\n본문")
    assert "<h1>" in html
    assert "제목" in html
    assert "<p>본문</p>" in html


def test_wikilink_becomes_anchor_with_data_link():
    html = render_markdown("관련: [[habix-profile]]")
    assert '<a' in html
    assert 'data-link="habix-profile"' in html
    assert ">habix-profile</a>" in html


def test_wikilink_with_subpath():
    html = render_markdown("[[260515_llm_wiki/prd]]")
    assert 'data-link="260515_llm_wiki/prd"' in html


def test_multiple_wikilinks_in_same_paragraph():
    html = render_markdown("[[alpha]] 그리고 [[beta]]")
    assert 'data-link="alpha"' in html
    assert 'data-link="beta"' in html


def test_code_block_wikilinks_preserved_as_text():
    # 코드 블록 안의 [[slug]]는 변환하지 않음
    html = render_markdown("```\n[[in-code]]\n```")
    assert 'data-link=' not in html
    assert "[[in-code]]" in html
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_render.py -v
```

Expected: 5 FAIL — module not found

- [ ] **Step 3: render.py 구현**

Create `wiki_app/render.py`:
```python
"""마크다운 → HTML 렌더. [[wikilink]]는 클릭 가능한 SPA 앵커로 후처리."""
from __future__ import annotations

import re

from markdown_it import MarkdownIt


_md = MarkdownIt("commonmark", {"breaks": False, "html": False}).enable("table")

# [[slug]] 또는 [[folder/slug]] — 영문/한글/숫자/-_/ 허용
_WIKILINK_RE = re.compile(r"\[\[([A-Za-z0-9가-힣_\-/]+)\]\]")

# 이미 렌더된 HTML에서 <code>/<pre> 블록 사이의 텍스트만 치환
_CODE_BLOCK_RE = re.compile(r"(<pre[^>]*>.*?</pre>|<code[^>]*>.*?</code>)", re.DOTALL)


def _replace_wikilinks_outside_code(html: str) -> str:
    """코드 블록을 보존하며 [[slug]]을 앵커로 치환한다."""
    parts = []
    last_end = 0
    for m in _CODE_BLOCK_RE.finditer(html):
        # 코드 블록 앞 부분은 변환
        outside = html[last_end:m.start()]
        parts.append(_WIKILINK_RE.sub(
            lambda mm: f'<a data-link="{mm.group(1)}" href="#page={mm.group(1)}">{mm.group(1)}</a>',
            outside,
        ))
        parts.append(m.group(0))  # 코드 블록은 그대로
        last_end = m.end()
    # 남은 꼬리 부분
    tail = html[last_end:]
    parts.append(_WIKILINK_RE.sub(
        lambda mm: f'<a data-link="{mm.group(1)}" href="#page={mm.group(1)}">{mm.group(1)}</a>',
        tail,
    ))
    return "".join(parts)


def render_markdown(body_md: str) -> str:
    """body_md를 HTML 문자열로 변환한다."""
    html = _md.render(body_md)
    return _replace_wikilinks_outside_code(html)
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_render.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add wiki_app/render.py tests/test_wiki_app_render.py
git commit -m "feat(wiki_app): render markdown + wikilink SPA anchor conversion"
```

---

## Task 3: search.py — 인덱스 빌드 + B 알고리즘

**Files:**
- Create: `wiki_app/search.py`
- Create: `tests/test_wiki_app_search.py`

`Index` 클래스를 서버 시작 시 한 번 빌드해서 메모리에 보관. `search(q)` 메서드가 점수 시스템으로 결과를 반환한다.

- [ ] **Step 1: 실패하는 테스트 작성 (B 알고리즘만)**

Create `tests/test_wiki_app_search.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from wiki_app.search import Index


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


@pytest.fixture(scope="module")
def index():
    return Index.build(wiki_root=WIKI_ROOT)


def test_index_loads_all_pages(index):
    assert index.total_pages >= 40
    assert "habix-profile" in index.by_slug


def test_search_title_match(index):
    results = index.search("habix")
    slugs = [r["slug"] for r in results["results"]]
    assert "habix-profile" in slugs
    assert results["expanded"] is False


def test_search_korean_description_match(index):
    # description은 한국어 — slug 매칭 불가지만 description 매칭 가능
    results = index.search("에이전트")
    assert results["total"] >= 4
    slugs = [r["slug"] for r in results["results"]]
    assert "agent-harness-pattern" in slugs


def test_search_tag_match(index):
    # ai-pm-role의 tags에 "ai-pm" 있음
    results = index.search("ai-pm")
    slugs = [r["slug"] for r in results["results"]]
    assert "ai-pm-role" in slugs


def test_search_score_ordering_title_first(index):
    # 제목에 "agent" 포함된 것이 description만 매칭되는 것보다 위
    results = index.search("agent")
    top_slugs = [r["slug"] for r in results["results"][:3]]
    # 슬러그에 agent 들어간 페이지가 상위 3개 안에 있어야 함
    assert any("agent" in s for s in top_slugs)


def test_search_returns_score_and_match_type(index):
    results = index.search("habix")
    first = results["results"][0]
    assert "score" in first
    assert "match_type" in first
    assert first["score"] > 0
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_search.py -v
```

Expected: 6 FAIL — module not found

- [ ] **Step 3: search.py 구현 (B 알고리즘만)**

Create `wiki_app/search.py`:
```python
"""검색 인덱스 + B 알고리즘 (Task 3) + C 확장 (Task 4)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter


@dataclass
class _Entry:
    slug: str
    category: str
    description: str  # index.md의 한 줄 설명
    tags: list[str] = field(default_factory=list)
    degree: int = 0  # inbound + outbound (정렬 tiebreaker)


# index.md 라인 예: "- [[habix-profile]] — 이든(김생근) 비즈니스 프로파일..."
_INDEX_LINE_RE = re.compile(r"^\s*-\s+\[\[([^\]]+)\]\]\s*—\s*(.*)$")
# 카테고리 헤더: "## concepts/ (20개)"
_INDEX_CAT_RE = re.compile(r"^##\s+(\w+)/")


class Index:
    def __init__(self, wiki_root: Path, by_slug: dict[str, _Entry]):
        self.wiki_root = wiki_root
        self.by_slug = by_slug
        self.total_pages = len(by_slug)

    @classmethod
    def build(cls, wiki_root: Path) -> "Index":
        """index.md + 각 페이지 frontmatter + graph.json 로드."""
        by_slug: dict[str, _Entry] = {}

        # 1. index.md에서 slug + category + description
        index_path = wiki_root / "index.md"
        current_cat = "concepts"
        for line in index_path.read_text().splitlines():
            mcat = _INDEX_CAT_RE.match(line)
            if mcat:
                current_cat = mcat.group(1)
                continue
            m = _INDEX_LINE_RE.match(line)
            if m:
                slug = m.group(1).strip()
                desc = m.group(2).strip()
                by_slug[slug] = _Entry(slug=slug, category=current_cat, description=desc)

        # 2. 각 페이지 frontmatter에서 tags 채움
        for entry in by_slug.values():
            md_path = wiki_root / entry.category / f"{entry.slug}.md"
            if md_path.exists():
                post = frontmatter.load(md_path)
                tags = post.metadata.get("tags") or []
                entry.tags = [str(t).lower() for t in tags]

        # 3. graph.json에서 degree
        graph_path = wiki_root / "graph.json"
        if graph_path.exists():
            graph = json.loads(graph_path.read_text())
            for n in graph["nodes"]:
                if n.get("kind") == "page" and n["id"] in by_slug:
                    by_slug[n["id"]].degree = n.get("inbound", 0) + n.get("outbound", 0)

        return cls(wiki_root=wiki_root, by_slug=by_slug)

    def search(self, query: str) -> dict:
        """B 알고리즘: 제목+desc+tags 점수 매칭."""
        q = query.strip().lower()
        if not q:
            return {"query": query, "results": [], "expanded": False, "total": 0}

        scored: list[tuple[int, str, _Entry]] = []
        for entry in self.by_slug.values():
            score = 0
            matched = []
            if q in entry.slug.lower():
                score += 3
                matched.append("title")
            if any(q in t for t in entry.tags):
                score += 2
                matched.append("tags")
            if q in entry.description.lower():
                score += 1
                matched.append("desc")
            if score > 0:
                scored.append((score, "+".join(matched), entry))

        # 점수 내림차순, 동점은 degree 내림차순
        scored.sort(key=lambda x: (-x[0], -x[2].degree, x[2].slug))

        results = [
            {
                "slug": e.slug,
                "category": e.category,
                "description": e.description,
                "score": score,
                "degree": e.degree,
                "match_type": match_type,
                "snippet": None,
            }
            for score, match_type, e in scored
        ]
        return {"query": query, "results": results, "expanded": False, "total": len(results)}
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_search.py -v
```

Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
git add wiki_app/search.py tests/test_wiki_app_search.py
git commit -m "feat(wiki_app): search Index + B algorithm (title+desc+tags scoring)"
```

---

## Task 4: search.py — C 확장 (본문 grep + snippet)

**Files:**
- Modify: `wiki_app/search.py` (Index.search에 확장 로직 추가)
- Modify: `tests/test_wiki_app_search.py` (확장 케이스 테스트 추가)

B 결과가 < 3개일 때 자동으로 본문 grep으로 확장. 매칭된 위치에서 ~80자 snippet 추출.

- [ ] **Step 1: 실패하는 테스트 추가**

Append to `tests/test_wiki_app_search.py`:
```python
def test_search_expands_when_fewer_than_3_results(index):
    # 매우 specific한 키워드 — B로는 적게 매칭됨
    results = index.search("ResNet")  # 본문에만 있고 description엔 없을 가능성
    # B 단계에서 0~2개 → C 확장 발동
    if results["expanded"]:
        assert results["total"] >= results.get("basic_total", 0)


def test_search_expansion_adds_snippet(index):
    # 결과 적은 쿼리에서 snippet이 채워지는지
    results = index.search("ResNet")
    if results["expanded"]:
        expanded = [r for r in results["results"] if r["snippet"]]
        if expanded:
            assert "ResNet" in expanded[0]["snippet"]


def test_search_no_expansion_when_3plus_results(index):
    # 많이 매칭되는 키워드 — 확장 안 함
    results = index.search("agent")
    if results["total"] >= 3:
        # B에서 3개 이상이면 확장 안 함 (basic_total 없음 또는 expanded=False)
        assert results["expanded"] is False
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_search.py -v
```

Expected: 3 new FAIL (기존 6 PASS는 유지)

- [ ] **Step 3: search.py에 확장 로직 추가**

Modify `wiki_app/search.py` — `Index.search` 메서드 끝부분 교체:

기존:
```python
        return {"query": query, "results": results, "expanded": False, "total": len(results)}
```

다음으로 교체:
```python
        # B 결과가 3개 미만이면 C 확장 발동
        if len(results) < 3:
            existing_slugs = {r["slug"] for r in results}
            expanded_results = self._body_grep(q, existing_slugs)
            if expanded_results:
                basic_total = len(results)
                results.extend(expanded_results)
                return {
                    "query": query,
                    "results": results,
                    "expanded": True,
                    "basic_total": basic_total,
                    "total": len(results),
                }

        return {"query": query, "results": results, "expanded": False, "total": len(results)}

    def _body_grep(self, q: str, exclude: set[str]) -> list[dict]:
        """본문 grep으로 추가 매칭. snippet 포함."""
        out: list[dict] = []
        for entry in self.by_slug.values():
            if entry.slug in exclude:
                continue
            md_path = self.wiki_root / entry.category / f"{entry.slug}.md"
            if not md_path.exists():
                continue
            text = md_path.read_text().lower()
            idx = text.find(q)
            if idx < 0:
                continue
            # 80자 snippet 추출
            start = max(0, idx - 30)
            end = min(len(text), idx + 50)
            snippet_raw = md_path.read_text()[start:end].replace("\n", " ")
            out.append({
                "slug": entry.slug,
                "category": entry.category,
                "description": entry.description,
                "score": 0,  # 본문 매칭은 점수 시스템 외
                "degree": entry.degree,
                "match_type": "body",
                "snippet": snippet_raw,
            })
        # degree 내림차순으로 일부 정렬
        out.sort(key=lambda r: -r["degree"])
        return out[:10]  # 최대 10개
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_search.py -v
```

Expected: 9 PASS (기존 6 + 신규 3)

- [ ] **Step 5: Commit**

```bash
git add wiki_app/search.py tests/test_wiki_app_search.py
git commit -m "feat(wiki_app): C expansion — body grep + snippet when results < 3"
```

---

## Task 5: access.py — access_count wrapper

**Files:**
- Create: `wiki_app/access.py`
- Create: `tests/test_wiki_app_access.py`

기존 `scripts/curate.py:record_access`를 import해서 백엔드에서 사용 가능하게 wrap.

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_wiki_app_access.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import frontmatter

from wiki_app.access import track


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


def test_track_increments_access_count(tmp_path, monkeypatch):
    # wiki 폴더를 복사한 임시 위치에서 테스트 (실제 wiki를 오염시키지 않기 위해)
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)

    test_page = test_wiki / "business" / "habix-profile.md"
    before = frontmatter.load(test_page).metadata.get("access_count", 0)

    track("habix-profile", wiki_root=test_wiki)

    after = frontmatter.load(test_page).metadata.get("access_count", 0)
    assert after == before + 1


def test_track_unknown_slug_does_not_raise(tmp_path, monkeypatch):
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)
    # 알 수 없는 slug — 조용히 skip (예외 X)
    track("nonexistent-slug-xyz", wiki_root=test_wiki)
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_access.py -v
```

Expected: 2 FAIL — module not found

- [ ] **Step 3: access.py 구현**

Create `wiki_app/access.py`:
```python
"""access_count 갱신 wrapper — scripts/curate.record_access 재사용."""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/ 를 sys.path에 추가 (기존 컨벤션)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import curate as _curate  # noqa: E402


def track(slug: str, wiki_root: Path | None = None) -> None:
    """페이지 조회 시 access_count를 1 증가시킨다.

    wiki_root 인자는 test 격리용. 기본은 curate.record_access의 cwd 기반 동작.
    """
    if wiki_root is not None:
        # curate.record_access는 cwd 기반이라 호출 직전에 cwd 변경
        import os
        original = os.getcwd()
        os.chdir(wiki_root.parent)
        try:
            _curate.record_access(slug)
        except Exception:
            # 알 수 없는 slug 등 — 조용히 skip
            pass
        finally:
            os.chdir(original)
    else:
        try:
            _curate.record_access(slug)
        except Exception:
            pass
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_access.py -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add wiki_app/access.py tests/test_wiki_app_access.py
git commit -m "feat(wiki_app): access.track wraps scripts/curate.record_access"
```

---

## Task 6: api.py — FastAPI app + 4 endpoints

**Files:**
- Create: `wiki_app/api.py`
- Create: `tests/test_wiki_app_api.py`

4개 endpoint(/api/index, /api/search, /api/page/{slug}, /api/ai-answer) + 정적 파일 마운트.

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_wiki_app_api.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from wiki_app.api import create_app


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


@pytest.fixture(scope="module")
def client():
    app = create_app(wiki_root=WIKI_ROOT)
    return TestClient(app)


def test_api_index_returns_metadata(client):
    r = client.get("/api/index")
    assert r.status_code == 200
    data = r.json()
    assert data["total_pages"] >= 40
    assert "categories" in data


def test_api_search_returns_results(client):
    r = client.get("/api/search", params={"q": "habix"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "habix"
    assert data["total"] > 0
    slugs = [r["slug"] for r in data["results"]]
    assert "habix-profile" in slugs


def test_api_search_empty_query(client):
    r = client.get("/api/search", params={"q": ""})
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_api_page_returns_html_and_metadata(client):
    r = client.get("/api/page/habix-profile")
    assert r.status_code == 200
    data = r.json()
    assert data["slug"] == "habix-profile"
    assert "<h1>" in data["html"]
    assert "frontmatter" in data
    assert "inbound" in data
    assert "outbound" in data


def test_api_page_unknown_slug_404(client):
    r = client.get("/api/page/nonexistent-xyz")
    assert r.status_code == 404


def test_api_ai_answer_stub(client):
    r = client.post("/api/ai-answer", json={
        "question": "test?",
        "context_slugs": ["habix-profile"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending"
    assert "🚧" in data["message"]
```

- [ ] **Step 2: 테스트 실패 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_api.py -v
```

Expected: 6 FAIL — module not found

- [ ] **Step 3: api.py 구현**

Create `wiki_app/api.py`:
```python
"""FastAPI app — 4 endpoints + static mount."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from wiki_app import access, pages, render, search


class AIAnswerRequest(BaseModel):
    question: str
    context_slugs: list[str] = []


def create_app(wiki_root: Path | None = None) -> FastAPI:
    """앱 팩토리 — wiki_root 인자로 test 격리 가능."""
    if wiki_root is None:
        wiki_root = Path(__file__).resolve().parent.parent / "wiki"

    app = FastAPI(title="LLM Wiki", version="0.1.0")
    index = search.Index.build(wiki_root=wiki_root)
    built_at = datetime.now(timezone.utc).isoformat()

    @app.get("/api/index")
    def api_index():
        cats = sorted({e.category for e in index.by_slug.values()})
        return {
            "total_pages": index.total_pages,
            "total_links": _count_links(wiki_root),
            "categories": cats,
            "last_built": built_at,
        }

    @app.get("/api/search")
    def api_search(q: str = ""):
        return index.search(q)

    @app.get("/api/page/{slug:path}")
    def api_page(slug: str):
        try:
            page = pages.load_page(slug, wiki_root=wiki_root)
        except pages.PageNotFound:
            raise HTTPException(status_code=404, detail=f"page not found: {slug}")
        # access_count 갱신 (조용히 실패)
        try:
            access.track(slug, wiki_root=wiki_root)
        except Exception:
            pass
        return {
            "slug": page["slug"],
            "title": page["frontmatter"].get("title", slug),
            "category": page["category"],
            "frontmatter": _sanitize_frontmatter(page["frontmatter"]),
            "html": render.render_markdown(page["body_md"]),
            "inbound": page["inbound"],
            "outbound": page["outbound"],
        }

    @app.post("/api/ai-answer")
    def api_ai_answer(req: AIAnswerRequest):
        return {
            "status": "pending",
            "message": "🚧 AI 답변은 다음 버전에서 활성화됩니다. CLI `/query`를 사용해주세요.",
            "question": req.question,
            "context_slugs": req.context_slugs,
        }

    # 정적 파일 마운트 (Task 7에서 추가될 static/index.html 등)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


def _count_links(wiki_root: Path) -> int:
    import json
    graph_path = wiki_root / "graph.json"
    if not graph_path.exists():
        return 0
    return len(json.loads(graph_path.read_text()).get("links", []))


def _sanitize_frontmatter(fm: dict) -> dict:
    """date 등 JSON 직렬화 불가 값 처리."""
    import datetime as _dt
    out = {}
    for k, v in fm.items():
        if isinstance(v, (_dt.date, _dt.datetime)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
```

- [ ] **Step 4: 테스트 통과 확인**

Run:
```bash
uv run pytest tests/test_wiki_app_api.py -v
```

Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
git add wiki_app/api.py tests/test_wiki_app_api.py
git commit -m "feat(wiki_app): FastAPI app — 4 endpoints (search/page/index/ai-answer stub)"
```

---

## Task 7: __main__.py — 서버 entry point

**Files:**
- Create: `wiki_app/__main__.py`

`uv run python -m wiki_app` 한 줄로 localhost:8000 서버 시작.

- [ ] **Step 1: __main__.py 작성**

Create `wiki_app/__main__.py`:
```python
"""uv run python -m wiki_app — localhost:8000에서 서버 시작."""
import uvicorn

from wiki_app.api import create_app


def main():
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 서버 시작 검증 (백그라운드)**

Run (background):
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python -m wiki_app &
SERVER_PID=$!
sleep 2
```

Expected: 콘솔에 `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Step 3: 4개 endpoint 수동 검증 (curl)**

Run:
```bash
curl -s http://127.0.0.1:8000/api/index | python3 -m json.tool
curl -s "http://127.0.0.1:8000/api/search?q=habix" | python3 -m json.tool | head -20
curl -s http://127.0.0.1:8000/api/page/habix-profile | python3 -m json.tool | head -10
curl -s -X POST http://127.0.0.1:8000/api/ai-answer -H 'Content-Type: application/json' -d '{"question":"test","context_slugs":[]}' | python3 -m json.tool
```

Expected: 모든 endpoint가 200 + 유효 JSON 반환

- [ ] **Step 4: 서버 종료**

Run:
```bash
kill $SERVER_PID
```

- [ ] **Step 5: Commit**

```bash
git add wiki_app/__main__.py
git commit -m "feat(wiki_app): __main__ entry point — uv run python -m wiki_app"
```

---

## Task 8: static/index.html — HTML 골격

**Files:**
- Create: `wiki_app/static/index.html`

검색창·결과 리스트·페이지 뷰의 빈 골격. JS가 dynamic하게 채움.

- [ ] **Step 1: HTML 작성**

Create `wiki_app/static/index.html`:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Wiki</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="topbar">
  <div class="brand">
    <span class="brand-mark">W</span>
    <span class="brand-name">LLM Wiki</span>
    <span class="brand-badge">내 머리 속의 두번째 뇌</span>
  </div>
  <div class="meta" id="meta">loading…</div>
</header>

<main id="app">
  <!-- 초기에 empty state, JS가 검색·결과에 따라 교체 -->
  <section id="view-empty" class="view view-empty">
    <h1>무엇을 찾고 계세요?</h1>
    <p class="subtitle">wiki에 쌓인 페이지에서 검색 · 필요하면 AI에게 추가로 물어보세요.</p>
    <form id="search-form" class="search-wrap">
      <input id="search-input" class="search-input" placeholder="에이전트, 관심 분야, hplan ..." autofocus autocomplete="off">
      <button type="submit" class="search-btn" aria-label="검색">🔍</button>
    </form>
    <div class="suggestions">
      <button class="suggestion" data-q="ai-pm-role">메가 허브: ai-pm-role</button>
      <button class="suggestion" data-q="omnimodality">최근 ingest: omnimodality</button>
      <button class="suggestion" data-q="">전체 인덱스</button>
    </div>
  </section>

  <section id="view-results" class="view view-results hidden">
    <header class="results-bar">
      <form id="search-form-2" class="search-wrap-compact">
        <input id="search-input-2" class="search-input-compact" autocomplete="off">
      </form>
      <span id="results-meta" class="results-meta"></span>
    </header>
    <div class="results-grid">
      <aside id="results-list" class="results-list"></aside>
      <article id="page-view" class="page-view">
        <div class="page-loading">페이지 선택</div>
      </article>
    </div>
  </section>

  <section id="view-empty-results" class="view view-empty-results hidden">
    <div class="empty-icon">🤔</div>
    <h2 id="empty-title">wiki에 직접 매칭되는 페이지가 없어요</h2>
    <p class="subtitle" id="empty-sub">자연어 질문 같은데, AI가 wiki 전체에서 관련 페이지를 찾아 답변할 수 있어요.</p>
    <button id="ai-cta-large" class="ai-cta-large">✨ AI에게 물어보기</button>
  </section>
</main>

<script src="/app.js" type="module"></script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add wiki_app/static/index.html
git commit -m "feat(wiki_app): static/index.html — search + results + empty views"
```

---

## Task 9: static/styles.css — Pretendard + 디자인 톤

**Files:**
- Create: `wiki_app/static/styles.css`

레퍼런스 `llm-wiki-demo.html`의 톤을 차용 + 검색·결과·페이지뷰 레이아웃.

- [ ] **Step 1: CSS 작성**

Create `wiki_app/static/styles.css`:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: #ffffff;
  color: #0d0d0d;
  -webkit-font-smoothing: antialiased;
  letter-spacing: -0.01em;
  height: 100vh;
  overflow: hidden;
}

/* Topbar */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px; border-bottom: 1px solid #f0f0f0;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand-mark {
  width: 28px; height: 28px; background: #0d0d0d; border-radius: 7px;
  color: white; font-weight: 700; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
}
.brand-name { font-weight: 600; font-size: 16px; }
.brand-badge {
  font-size: 11px; background: #f3f0ff; color: #5e3fcf;
  padding: 3px 9px; border-radius: 10px; font-weight: 500;
}
.meta { font-size: 12px; color: #888; }

/* Empty state */
.view-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 80px 24px;
}
.view-empty h1 { font-size: 32px; font-weight: 700; margin-bottom: 10px; letter-spacing: -0.02em; }
.view-empty .subtitle { font-size: 16px; color: #6e6e6e; margin-bottom: 36px; }

.search-wrap { max-width: 560px; width: 100%; position: relative; }
.search-input {
  width: 100%; padding: 16px 56px 16px 22px; border: 1px solid #d9d9d9;
  border-radius: 24px; font-size: 15px; font-family: inherit; outline: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.search-input:focus { border-color: #0d0d0d; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.search-btn {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  width: 36px; height: 36px; border-radius: 50%; background: #0d0d0d;
  border: none; color: white; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}

.suggestions { display: flex; gap: 8px; margin-top: 20px; flex-wrap: wrap; justify-content: center; }
.suggestion {
  font-size: 12px; padding: 6px 12px; background: #f5f5f5; border: none;
  border-radius: 14px; cursor: pointer; color: #555;
}
.suggestion:hover { background: #ececec; }

/* Results view */
.view-results { height: calc(100vh - 57px); display: flex; flex-direction: column; }
.results-bar {
  display: flex; align-items: center; gap: 14px; padding: 10px 24px;
  border-bottom: 1px solid #f0f0f0;
}
.search-wrap-compact { flex: 1; max-width: 600px; }
.search-input-compact {
  width: 100%; padding: 8px 16px; border: 1px solid #d9d9d9;
  border-radius: 18px; font-size: 13px; font-family: inherit; outline: none;
}
.results-meta { font-size: 11px; color: #888; }

.results-grid { flex: 1; display: flex; min-height: 0; }
.results-list { width: 320px; overflow-y: auto; border-right: 1px solid #eee; padding: 8px; }
.result-card {
  padding: 12px; margin-bottom: 4px; border-radius: 8px; cursor: pointer;
  border: 1px solid transparent;
}
.result-card:hover { background: #fafafa; }
.result-card.active { background: #f0f6fc; border-left: 3px solid #2563eb; padding-left: 9px; }
.result-card-title { font-weight: 600; font-size: 13px; }
.result-card-desc { color: #666; font-size: 11px; margin-top: 4px; line-height: 1.5; }
.result-card-meta { color: #888; font-size: 10px; margin-top: 6px; }
.result-card-snippet {
  background: #fffbeb; padding: 4px 6px; margin-top: 5px;
  font-size: 10px; font-style: italic; color: #92500e; border-radius: 3px;
}
.result-card-snippet mark { background: #fde68a; padding: 0 2px; }

/* Page view */
.page-view { flex: 1; overflow-y: auto; padding: 24px 32px; }
.page-view h1 { font-size: 24px; margin-bottom: 8px; }
.page-view .page-meta { font-size: 11px; color: #888; margin-bottom: 16px; }
.page-view .ai-toggle-row {
  display: flex; justify-content: flex-end; margin-bottom: 12px;
}
.ai-toggle {
  font-size: 12px; padding: 6px 12px; background: white;
  border: 1px solid #d9d9d9; border-radius: 14px; cursor: pointer; color: #666;
}
.ai-toggle:hover { background: #fafafa; }
.page-content { font-size: 14px; line-height: 1.75; color: #1a1a1a; }
.page-content h1 { font-size: 22px; margin: 20px 0 10px; }
.page-content h2 { font-size: 18px; margin: 18px 0 8px; }
.page-content h3 { font-size: 16px; margin: 14px 0 6px; }
.page-content p { margin-bottom: 10px; }
.page-content ul, .page-content ol { margin: 8px 0 12px 22px; }
.page-content table { border-collapse: collapse; margin: 12px 0; font-size: 13px; }
.page-content th, .page-content td { border: 1px solid #e5e5e5; padding: 6px 10px; }
.page-content th { background: #fafafa; font-weight: 600; }
.page-content a[data-link] {
  color: #2563eb; text-decoration: underline; cursor: pointer;
}
.page-content code { background: #f5f5f5; padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }
.page-content pre { background: #fafafa; padding: 12px; border-radius: 6px; overflow-x: auto; }
.page-content pre code { background: none; padding: 0; }

/* AI CTA - 부족 결과 (노란 박스) */
.ai-cta-box {
  margin-top: 16px; padding: 16px; background: #fffbf0;
  border: 1px solid #fcd34d; border-radius: 10px;
}
.ai-cta-box-title { font-size: 13px; font-weight: 600; color: #92500e; margin-bottom: 6px; }
.ai-cta-box-desc { font-size: 12px; color: #78350f; line-height: 1.6; margin-bottom: 10px; }
.ai-cta-box-btn {
  font-size: 12px; padding: 8px 14px; background: #0d0d0d; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-weight: 500;
}

/* AI CTA - empty state */
.view-empty-results {
  display: flex; flex-direction: column; align-items: center;
  padding: 80px 24px; text-align: center;
}
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.view-empty-results h2 { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.ai-cta-large {
  margin-top: 16px; font-size: 13px; padding: 12px 22px;
  background: #0d0d0d; color: white; border: none; border-radius: 10px;
  cursor: pointer; font-weight: 500;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Expansion notice */
.expansion-notice {
  background: #faf5ff; color: #7c3aed; padding: 6px 10px;
  font-size: 11px; border-radius: 6px; margin: 8px;
}

.hidden { display: none !important; }
```

- [ ] **Step 2: Commit**

```bash
git add wiki_app/static/styles.css
git commit -m "feat(wiki_app): static/styles.css — Pretendard + reference design tones"
```

---

## Task 10: static/app.js — 검색 + 결과 리스트 + URL hash

**Files:**
- Create: `wiki_app/static/app.js`

상태 관리, 검색 fetch, 결과 카드 렌더, URL hash 동기화.

- [ ] **Step 1: app.js 작성 (검색 + 결과 렌더만, 페이지뷰는 Task 11)**

Create `wiki_app/static/app.js`:
```js
// 전역 상태
const state = {
  query: "",
  results: [],
  expanded: false,
  basicTotal: 0,
  selectedSlug: null,
  pageData: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  meta: $("#meta"),
  viewEmpty: $("#view-empty"),
  viewResults: $("#view-results"),
  viewEmptyResults: $("#view-empty-results"),
  searchForm: $("#search-form"),
  searchInput: $("#search-input"),
  searchForm2: $("#search-form-2"),
  searchInput2: $("#search-input-2"),
  resultsMeta: $("#results-meta"),
  resultsList: $("#results-list"),
  pageView: $("#page-view"),
  emptyTitle: $("#empty-title"),
  emptySub: $("#empty-sub"),
  aiCtaLarge: $("#ai-cta-large"),
};

// --- 초기 로드 ---
async function init() {
  // 메타 정보
  try {
    const r = await fetch("/api/index");
    const data = await r.json();
    els.meta.textContent = `${data.total_pages} pages · ${data.total_links} links`;
  } catch (e) {
    els.meta.textContent = "오프라인";
  }

  // suggestion 버튼
  $$(".suggestion").forEach(b => {
    b.addEventListener("click", () => {
      const q = b.dataset.q || "";
      els.searchInput.value = q;
      doSearch(q);
    });
  });

  // 검색 폼
  els.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    doSearch(els.searchInput.value);
  });
  els.searchForm2.addEventListener("submit", (e) => {
    e.preventDefault();
    doSearch(els.searchInput2.value);
  });

  // empty state AI CTA
  els.aiCtaLarge.addEventListener("click", () => callAI(state.query, []));

  // hashchange 처리 (Task 11에서 페이지 로드)
  window.addEventListener("hashchange", handleHash);
  handleHash();
}

// --- 검색 ---
async function doSearch(query) {
  query = (query || "").trim();
  state.query = query;
  if (!query) {
    showEmpty();
    return;
  }
  const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const data = await r.json();
  state.results = data.results;
  state.expanded = data.expanded || false;
  state.basicTotal = data.basic_total || data.total;

  // URL hash 갱신
  setHash({ q: query, page: null });

  if (data.total === 0) {
    showEmptyResults(query);
  } else {
    showResults();
  }
}

function showEmpty() {
  els.viewEmpty.classList.remove("hidden");
  els.viewResults.classList.add("hidden");
  els.viewEmptyResults.classList.add("hidden");
}

function showResults() {
  els.viewEmpty.classList.add("hidden");
  els.viewResults.classList.remove("hidden");
  els.viewEmptyResults.classList.add("hidden");
  els.searchInput2.value = state.query;

  const metaText = state.expanded
    ? `${state.results.length}개 (본문 grep까지 확장)`
    : `${state.results.length}개 매칭`;
  els.resultsMeta.textContent = metaText;

  renderResultList();

  // 첫 카드 자동 선택
  if (state.results.length > 0) {
    selectPage(state.results[0].slug);
  }
}

function showEmptyResults(query) {
  els.viewEmpty.classList.add("hidden");
  els.viewResults.classList.add("hidden");
  els.viewEmptyResults.classList.remove("hidden");
  els.emptyTitle.textContent = "wiki에 직접 매칭되는 페이지가 없어요";
  els.emptySub.textContent = `"${query}" — AI가 wiki 전체에서 관련 페이지를 찾아 답변할 수 있어요.`;
}

function renderResultList() {
  const html = [];
  if (state.expanded) {
    html.push(`<div class="expansion-notice">🔍 결과가 적어 본문까지 자동 검색 — ${state.results.length - state.basicTotal}개 추가</div>`);
  }
  for (const r of state.results) {
    const isActive = r.slug === state.selectedSlug ? "active" : "";
    const snippet = r.snippet
      ? `<div class="result-card-snippet">${highlight(r.snippet, state.query)}</div>`
      : "";
    html.push(`
      <div class="result-card ${isActive}" data-slug="${r.slug}">
        <div class="result-card-title">${r.slug}</div>
        <div class="result-card-desc">${escapeHtml(r.description || "")}</div>
        <div class="result-card-meta">${r.category} · degree ${r.degree} · ${r.match_type}</div>
        ${snippet}
      </div>
    `);
  }
  els.resultsList.innerHTML = html.join("");
  els.resultsList.querySelectorAll(".result-card").forEach(card => {
    card.addEventListener("click", () => selectPage(card.dataset.slug));
  });
}

function highlight(text, query) {
  const escaped = escapeHtml(text);
  if (!query) return escaped;
  const re = new RegExp(`(${query.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
  return escaped.replace(re, '<mark>$1</mark>');
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

// --- URL hash ---
function setHash({ q, page }) {
  const parts = [];
  if (q) parts.push(`q=${encodeURIComponent(q)}`);
  if (page) parts.push(`page=${encodeURIComponent(page)}`);
  const newHash = parts.length ? "#" + parts.join("&") : "";
  if (location.hash !== newHash) history.pushState(null, "", newHash || location.pathname);
}

function readHash() {
  const h = location.hash.slice(1);
  const out = {};
  for (const pair of h.split("&")) {
    const [k, v] = pair.split("=");
    if (k) out[k] = decodeURIComponent(v || "");
  }
  return out;
}

async function handleHash() {
  const { q, page } = readHash();
  if (q && q !== state.query) {
    els.searchInput.value = q;
    els.searchInput2.value = q;
    await doSearch(q);
  }
  if (page && page !== state.selectedSlug) {
    await selectPage(page);
  }
}

// --- 페이지 선택 (Task 11에서 구현) ---
async function selectPage(slug) {
  state.selectedSlug = slug;
  setHash({ q: state.query, page: slug });
  renderResultList();
  // TODO Task 11: 페이지 fetch + 렌더
  els.pageView.innerHTML = `<div class="page-loading">페이지 로드 중: ${slug}</div>`;
}

// --- AI 호출 (Task 12에서 구현) ---
async function callAI(question, contextSlugs) {
  // TODO Task 12: 백엔드 호출 + 응답 표시
  alert(`AI 호출 (stub): ${question}`);
}

init();
```

- [ ] **Step 2: 수동 검증 — 검색 작동 확인**

Run:
```bash
uv run python -m wiki_app &
SERVER_PID=$!
sleep 2
# Playwright MCP 또는 브라우저로 http://127.0.0.1:8000 접속
# 1. 빈 상태 표시
# 2. "habix" 검색 → 결과 카드 표시
# 3. URL hash가 #q=habix로 갱신
# 4. 카드 클릭 → URL #q=habix&page=habix-profile로 갱신 (페이지 로드 stub만)
kill $SERVER_PID
```

Expected: 위 4가지 동작 모두 확인. 페이지 본문은 아직 stub.

- [ ] **Step 3: Commit**

```bash
git add wiki_app/static/app.js
git commit -m "feat(wiki_app): app.js — search + results + URL hash sync"
```

---

## Task 11: static/app.js — 페이지 뷰 + wikilink 클릭

**Files:**
- Modify: `wiki_app/static/app.js` (selectPage 구현 + wikilink 클릭 핸들러)

- [ ] **Step 1: selectPage 구현 + wikilink 클릭 핸들러 교체**

Modify `wiki_app/static/app.js` — `selectPage` 함수를 다음으로 교체:

```js
async function selectPage(slug) {
  state.selectedSlug = slug;
  setHash({ q: state.query, page: slug });
  renderResultList();

  els.pageView.innerHTML = `<div class="page-loading">로드 중…</div>`;
  try {
    const r = await fetch(`/api/page/${slug}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    state.pageData = await r.json();
    renderPage();
  } catch (e) {
    els.pageView.innerHTML = `<div class="page-loading">오류: ${e.message}</div>`;
  }
}

function renderPage() {
  const p = state.pageData;
  if (!p) return;
  const tags = (p.frontmatter.tags || []).map(t => `<span class="result-card-meta">#${t}</span>`).join(" ");
  els.pageView.innerHTML = `
    <div class="ai-toggle-row">
      <button class="ai-toggle" id="ai-toggle-btn">✨ AI 답변</button>
    </div>
    <h1>${escapeHtml(p.title)}</h1>
    <div class="page-meta">
      ${p.category} · in ${p.inbound} / out ${p.outbound} · access ${p.frontmatter.access_count || 0} · ${tags}
    </div>
    <div class="page-content">${p.html}</div>
    ${maybeAiCtaBox()}
  `;
  // wikilink 클릭 위임
  els.pageView.querySelectorAll("a[data-link]").forEach(a => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      selectPage(a.dataset.link);
    });
  });
  // AI 토글 (Task 12)
  const aiBtn = $("#ai-toggle-btn");
  if (aiBtn) {
    aiBtn.addEventListener("click", () => {
      const slugs = state.results.map(r => r.slug).slice(0, 5);
      callAI(state.query || p.title, slugs);
    });
  }
  // AI CTA box (결과 부족 시)
  const ctaBtn = $("#ai-cta-box-btn");
  if (ctaBtn) {
    ctaBtn.addEventListener("click", () => {
      const slugs = state.results.map(r => r.slug);
      callAI(state.query, slugs);
    });
  }
}

function maybeAiCtaBox() {
  // 결과 < 3개일 때만 결과 영역 아래에 큰 박스 CTA
  if (state.results.length > 0 && state.results.length < 3) {
    return `
      <div class="ai-cta-box">
        <div class="ai-cta-box-title">✨ 결과가 충분하지 않으신가요?</div>
        <div class="ai-cta-box-desc">위 ${state.results.length}개 페이지를 컨텍스트로 AI가 직접 답변해드릴 수 있어요.</div>
        <button id="ai-cta-box-btn" class="ai-cta-box-btn">"${escapeHtml(state.query)}" — AI에게 물어보기 →</button>
      </div>
    `;
  }
  return "";
}
```

- [ ] **Step 2: 수동 검증**

Run:
```bash
uv run python -m wiki_app &
SERVER_PID=$!
sleep 2
# 브라우저에서 http://127.0.0.1:8000 접속:
# 1. "habix" 검색 → habix-profile 카드 자동 선택
# 2. 우측 패널에 페이지 본문 (h1, frontmatter meta, html) 표시
# 3. 본문 내 [[wikilink]] 클릭 → 같은 화면에서 우측만 교체, 좌측 결과 유지
# 4. URL hash가 #q=habix&page=context-dealer-pattern로 갱신
# 5. 새로고침 시 상태 복원
kill $SERVER_PID
```

Expected: 5가지 모두 작동. wikilink 클릭이 좌측 검색 결과 그대로 유지.

- [ ] **Step 3: Commit**

```bash
git add wiki_app/static/app.js
git commit -m "feat(wiki_app): page view rendering + wikilink in-page navigation"
```

---

## Task 12: static/app.js — AI 토글 + CTA 차등화 (stub 응답)

**Files:**
- Modify: `wiki_app/static/app.js` (callAI 실제 fetch + 응답 표시)

- [ ] **Step 1: callAI 구현 교체**

Modify `wiki_app/static/app.js` — `callAI` 함수를 다음으로 교체:

```js
async function callAI(question, contextSlugs) {
  // 모달 또는 페이지 영역에 응답 표시
  const modal = ensureAiModal();
  modal.classList.remove("hidden");
  modal.querySelector(".ai-modal-body").innerHTML =
    '<div class="ai-modal-loading">AI 답변 요청 중...</div>';

  try {
    const r = await fetch("/api/ai-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context_slugs: contextSlugs }),
    });
    const data = await r.json();
    modal.querySelector(".ai-modal-body").innerHTML = `
      <div class="ai-modal-question">Q: ${escapeHtml(data.question)}</div>
      <div class="ai-modal-status">${escapeHtml(data.message)}</div>
      <div class="ai-modal-context">컨텍스트: ${(data.context_slugs || []).map(s => `<code>${s}</code>`).join(", ") || "(없음)"}</div>
    `;
  } catch (e) {
    modal.querySelector(".ai-modal-body").innerHTML =
      `<div class="ai-modal-status">오류: ${e.message}</div>`;
  }
}

function ensureAiModal() {
  let modal = document.getElementById("ai-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "ai-modal";
  modal.className = "ai-modal hidden";
  modal.innerHTML = `
    <div class="ai-modal-card">
      <button class="ai-modal-close" aria-label="닫기">×</button>
      <h3>✨ AI 답변</h3>
      <div class="ai-modal-body"></div>
    </div>
  `;
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
  });
  modal.querySelector(".ai-modal-close").addEventListener("click", () => modal.classList.add("hidden"));
  document.body.appendChild(modal);
  return modal;
}
```

- [ ] **Step 2: AI 모달 스타일 추가**

Append to `wiki_app/static/styles.css`:
```css
/* AI modal */
.ai-modal {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.ai-modal-card {
  background: white; border-radius: 14px; padding: 24px;
  max-width: 560px; width: 90%; position: relative;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.ai-modal-card h3 { font-size: 16px; margin-bottom: 14px; }
.ai-modal-close {
  position: absolute; top: 14px; right: 16px; background: none;
  border: none; font-size: 22px; cursor: pointer; color: #888;
}
.ai-modal-question { font-size: 13px; color: #1a1a1a; margin-bottom: 10px; font-weight: 500; }
.ai-modal-status {
  background: #fff8e1; border: 1px solid #fcd34d; border-radius: 8px;
  padding: 12px 14px; font-size: 13px; color: #92500e; margin-bottom: 12px;
}
.ai-modal-context { font-size: 11px; color: #666; }
.ai-modal-context code { background: #f5f5f5; padding: 1px 5px; border-radius: 3px; }
.ai-modal-loading { text-align: center; padding: 16px; color: #888; font-size: 13px; }
```

- [ ] **Step 3: 수동 검증 — 3가지 AI CTA 모두 동작**

Run:
```bash
uv run python -m wiki_app &
SERVER_PID=$!
sleep 2
# 브라우저에서:
# 1. "habix" 검색 → 충분 결과 → 페이지 상단 "✨ AI 답변" 작은 버튼 클릭 → 모달 stub 응답
# 2. "ResNet 같은 적게 매칭되는 키워드" 검색 → 결과 부족 → 노란 CTA 박스 → 클릭 → 모달
# 3. "내일 어떻게 할까" 검색 → 0개 → empty state → 큰 검정 버튼 클릭 → 모달
kill $SERVER_PID
```

Expected: 3가지 시나리오 모두 모달 stub 응답 표시. 메시지에 "🚧 준비 중" 포함.

- [ ] **Step 4: Commit**

```bash
git add wiki_app/static/app.js wiki_app/static/styles.css
git commit -m "feat(wiki_app): AI toggle + CTA tiered modal with stub response"
```

---

## Task 13: 통합 검증 — DoD 체크

**Files:** (수정 없음, 검증만)

design doc §9의 10개 체크박스를 모두 확인.

- [ ] **Step 1: 서버 시작**

Run:
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python -m wiki_app &
SERVER_PID=$!
sleep 2
```

Expected: `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Step 2: 전체 테스트 swap 통과**

Run:
```bash
uv run pytest tests/ -v
```

Expected: 모든 테스트 PASS (기존 + wiki_app 신규 ~20개)

- [ ] **Step 3: DoD 체크리스트**

브라우저로 `http://127.0.0.1:8000` 접속해 다음 모두 확인:

| # | 항목 | 확인 |
|---|---|---|
| 1 | `uv run python -m wiki_app` 한 줄로 서버 시작 | □ |
| 2 | 빈 상태 (검색창 + 추천 키워드 3개) | □ |
| 3 | "에이전트" 검색 → 결과 6+개 (B 알고리즘) | □ |
| 4 | "ResNet" 등 적은 매칭 쿼리 → 자동 확장 발동 + 보라색 안내 | □ |
| 5 | 결과 0개 쿼리 → 큰 AI CTA empty state | □ |
| 6 | 카드 클릭 → 우측 패널 페이지 본문 + access_count 1 증가 | □ |
| 7 | `[[wikilink]]` 클릭 → 우측만 교체, 좌측 검색 결과 유지 | □ |
| 8 | URL hash 새로고침 시 상태 복원 | □ |
| 9 | AI 토글 클릭 → stub 모달 "🚧 준비 중" | □ |
| 10 | 한국어("에이전트") + 영문("agent") 모두 매칭 | □ |

체크: access_count 증가는 페이지 마크다운 파일 frontmatter 확인.
```bash
grep "access_count:" wiki/business/habix-profile.md
```

- [ ] **Step 4: 서버 종료**

```bash
kill $SERVER_PID
```

- [ ] **Step 5: 최종 commit (선택)**

DoD 모두 통과했으면:
```bash
git log --oneline | head -15  # Task 0~12 commit 13개 확인
```

추가 정리 commit이 있으면:
```bash
git commit -m "chore(wiki_app): MVP integration verified, 13 tasks complete"
```

---

## Self-Review 결과

**1. Spec coverage:** design doc §2 목표 9개 모두 task로 매핑됨
- 검색 (B+desc+tags) → Task 3 ✓
- < 3개 자동 확장 (C) → Task 4 ✓
- 페이지 뷰 + wikilink → Task 11 ✓
- access_count → Task 5+6 ✓
- AI 토글 stub → Task 6+12 ✓
- CTA 차등화 → Task 12 + `maybeAiCtaBox` 함수 ✓
- URL hash → Task 10 ✓
- 한국어 매칭 → Task 3 (description/tags 매칭 자동) ✓
- 로컬 서버 한 줄 시작 → Task 7 ✓

**2. Placeholder scan:** 모든 step에 실제 코드 + 명령 포함. TBD/TODO/"적절히 처리" 없음.

**3. Type consistency:**
- API JSON 응답 (search/page/ai-answer) — design doc §7과 일치
- `match_type` 값: "title", "tags", "desc", "body", 또는 "+" 조합 — Task 3/4 일관
- frontend `state` 객체 필드명 — 모든 task에서 동일 사용

**4. Scope check:** 13개 task, 각 5-step, 총 약 65 step. TDD 백엔드 + 수동검증 frontend. 1차 MVP에 적합한 크기.
