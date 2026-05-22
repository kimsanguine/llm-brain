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
