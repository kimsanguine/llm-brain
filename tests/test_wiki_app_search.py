import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from wiki_app.search import Index


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


@pytest.fixture(scope="module")
def index():
    return Index.build(wiki_root=WIKI_ROOT)


def _build_wiki(tmp_path, pages, index_body):
    """tmp_path 안에 wiki_root + 부모의 index.md 를 만든다.

    Index.build 는 index.md 를 wiki_root.parent 에서 읽으므로 그 레이아웃을 그대로 재현.
    pages: {category: {slug: file_content}}, index_body: index.md 전문.
    반환: wiki_root Path.
    """
    project_root = tmp_path / "proj"
    wiki_root = project_root / "wiki"
    for category, slug_map in pages.items():
        cat_dir = wiki_root / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        for slug, content in slug_map.items():
            (cat_dir / f"{slug}.md").write_text(content)
    (project_root / "index.md").write_text(index_body)
    return wiki_root


def test_index_loads_all_pages(index):
    assert index.total_pages >= 40
    assert "habix-profile" in index.by_slug


def test_search_title_match(index):
    results = index.search("habix")
    slugs = [r["slug"] for r in results["results"]]
    assert "habix-profile" in slugs


def test_search_korean_description_match(tmp_path):
    # WHY: slug 은 영문이라 한국어 쿼리로 매칭 안 되지만, index.md description
    # 또는 frontmatter page_title 의 한국어는 매칭돼야 한다. 특정 작성자 slug
    # ("agent-harness-pattern") 가 아니라 "한국어 본문이 description/title 로
    # 매칭된다"는 로직을 self-contained 로 검증.
    index_body = (
        "## concepts/ (2개)\n"
        "- [[harness-pattern]] — 에이전트 하네스 설계 패턴 정리\n"
        "- [[other-topic]] — 전혀 다른 주제 설명\n"
    )
    pages = {
        "concepts": {
            "harness-pattern": (
                "---\ntitle: 에이전트 하네스 패턴\ntags: [agent, harness]\n---\n# 본문\n"
            ),
            "other-topic": (
                "---\ntitle: Other Topic\ntags: [misc]\n---\n# 본문\n"
            ),
        },
    }
    idx = Index.build(wiki_root=_build_wiki(tmp_path, pages, index_body))

    # 한국어 "에이전트" 는 영문 slug 엔 없지만 description + page_title 에 있다.
    results = idx.search("에이전트")
    slugs = [r["slug"] for r in results["results"]]
    assert "harness-pattern" in slugs
    # 한국어 매칭이 없는 페이지는 빠져야 한다 (false positive 방지).
    assert "other-topic" not in slugs
    # description(+1) + page_title(+3) 둘 다 매칭이라 점수가 desc-only(1) 보다 높다.
    hit = next(r for r in results["results"] if r["slug"] == "harness-pattern")
    assert "page_title" in hit["match_type"]


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


# --- 버그 4 회귀: 깨진 페이지 1개가 전체 인덱스 빌드를 크래시시키지 않는다 ---
# WHY: Index.build 는 페이지별 frontmatter.load 중 한 페이지의 invalid YAML 로
# 전체가 죽으면 안 된다. 깨진 페이지는 skip 하고 나머지는 정상 인덱싱돼야 한다.


def test_index_build_skips_broken_page_and_indexes_rest(tmp_path):
    index_body = (
        "## concepts/ (3개)\n"
        "- [[good-one]] — 정상 페이지 하나\n"
        "- [[broken-one]] — 깨진 YAML 페이지\n"
        "- [[good-two]] — 또 다른 정상 페이지\n"
    )
    pages = {
        "concepts": {
            "good-one": "---\ntitle: Good One\ntags: [alpha]\n---\n# Good One\n",
            # invalid YAML: 닫히지 않은 따옴표 + 깨진 들여쓰기
            "broken-one": "---\ntitle: \"unterminated\ntags: [a, b\n  : : :\n---\n# Broken\n",
            "good-two": "---\ntitle: Good Two\ntags: [beta]\n---\n# Good Two\n",
        },
    }
    wiki_root = _build_wiki(tmp_path, pages, index_body)

    # 빌드가 예외 없이 끝나야 한다 (크래시 격리).
    idx = Index.build(wiki_root=wiki_root)

    # 세 slug 모두 index.md 기반으로 등록은 된다 (description/category 보존).
    assert set(idx.by_slug) == {"good-one", "broken-one", "good-two"}
    # 정상 페이지는 frontmatter title/tags 가 채워진다.
    assert idx.by_slug["good-one"].page_title == "Good One"
    assert idx.by_slug["good-two"].page_title == "Good Two"
    assert "alpha" in idx.by_slug["good-one"].tags
    # 깨진 페이지는 frontmatter 메타 없이 skip — title 비고 tags 비어있음.
    assert idx.by_slug["broken-one"].page_title == ""
    assert idx.by_slug["broken-one"].tags == []
    # 정상 페이지 검색은 정상 작동.
    good_slugs = [r["slug"] for r in idx.search("Good One")["results"]]
    assert "good-one" in good_slugs
