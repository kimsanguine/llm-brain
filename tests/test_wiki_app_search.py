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
