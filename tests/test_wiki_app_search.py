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
