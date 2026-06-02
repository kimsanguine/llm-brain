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


# --- path traversal 회귀 (Codex [high]): wiki_root 밖 파일 접근 차단 ---
# 이 테스트들은 사용자 wiki 데이터에 의존하지 않도록 tmp_path 로 격리된
# wiki 구조를 직접 만든다. (conftest 의 wiki-dependent skip 은 파일명 기준이라
# 사용자 wiki 부재 시 skip 될 수 있으나, 테스트 자체는 자기완결적이다.)


@pytest.fixture
def isolated_wiki(tmp_path):
    """wiki_root 와 그 바깥에 secret 파일을 둔 격리 구조."""
    wiki_root = tmp_path / "wiki"
    (wiki_root / "concepts").mkdir(parents=True)
    (wiki_root / "concepts" / "real-page.md").write_text(
        "---\ntitle: Real\n---\n# Real\n"
    )
    # 정당한 중첩 페이지 (slug 에 '/' 포함) — 허용되어야 함
    (wiki_root / "projects" / "260515_llm_wiki").mkdir(parents=True)
    (wiki_root / "projects" / "260515_llm_wiki" / "prd.md").write_text(
        "---\ntitle: PRD\n---\n# PRD\n"
    )
    # wiki_root 밖(부모) 의 비밀 파일 — traversal 로 도달 시도 대상
    (tmp_path / "CLAUDE.md").write_text("# SECRET outside wiki\n")
    return wiki_root


@pytest.mark.parametrize(
    "evil_slug",
    [
        "../../CLAUDE",          # 리포 루트 CLAUDE.md 노출 재현 케이스
        "../CLAUDE",             # 한 단계 상위
        "../../../etc/passwd",   # 시스템 파일
        "/etc/passwd",           # 선행 '/' 절대경로
    ],
)
def test_find_page_path_rejects_traversal(isolated_wiki, evil_slug):
    # wiki_root 밖으로 나가는 slug 는 파일이 실재해도 PageNotFound 여야 한다.
    with pytest.raises(PageNotFound):
        find_page_path(evil_slug, wiki_root=isolated_wiki)


def test_find_page_path_allows_legit_single_slug(isolated_wiki):
    p = find_page_path("real-page", wiki_root=isolated_wiki)
    assert p.name == "real-page.md"
    assert p.parent.name == "concepts"


def test_find_page_path_allows_legit_nested_slug(isolated_wiki):
    # slug 에 '/' 가 있어도 wiki_root 안이면 허용 — "'/' 있으면 거부"는 틀린 fix.
    p = find_page_path("260515_llm_wiki/prd", wiki_root=isolated_wiki)
    assert p.name == "prd.md"
    assert p.parent.name == "260515_llm_wiki"
