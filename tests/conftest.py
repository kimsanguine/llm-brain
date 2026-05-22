import json
from pathlib import Path

import pytest


_WIKI_ROOT = Path(__file__).parent.parent / "wiki"
# wiki 데이터 존재 체크: wiki/concepts/ 안에 .md 페이지가 1개 이상 있어야 사용자 환경
# (index.md는 프로젝트 루트에 위치하므로 wiki/ 안엔 없음)
_HAS_USER_WIKI = (
    _WIKI_ROOT.exists()
    and (_WIKI_ROOT / "concepts").exists()
    and any((_WIKI_ROOT / "concepts").glob("*.md"))
)


def pytest_collection_modifyitems(config, items):
    """wiki-dependent tests를 사용자 wiki 데이터 없을 때 자동 skip (CI/공개 레포 호환).

    wiki/ 는 .gitignore 되어 있어 CI 러너 또는 fresh clone 환경엔 wiki 데이터가 없다.
    `tests/test_wiki_app_{access,api,pages,search}.py` 들은 wiki/index.md +
    실제 마크다운 페이지를 직접 읽어 검증하므로, 데이터 없으면 skip.
    `test_wiki_app_render` 는 wiki 데이터 의존이 없어 항상 실행.
    """
    if _HAS_USER_WIKI:
        return
    skip = pytest.mark.skip(reason="requires user wiki data (wiki/ is gitignored)")
    wiki_dependent = (
        "test_wiki_app_access",
        "test_wiki_app_api",
        "test_wiki_app_pages",
        "test_wiki_app_search",
    )
    for item in items:
        fname = Path(str(item.fspath)).name
        if any(fname.startswith(m) for m in wiki_dependent):
            item.add_marker(skip)


GRAPH_STUB = {
    "nodes": [
        {"id": "alpha", "kind": "page", "title": "Alpha", "type": "concept",
         "category": "concepts", "domain": [], "tags": [], "inbound": 2, "outbound": 1},
        {"id": "beta",  "kind": "page", "title": "Beta",  "type": "concept",
         "category": "concepts", "domain": [], "tags": [], "inbound": 1, "outbound": 0},
        {"id": "gamma", "kind": "page", "title": "Gamma", "type": "concept",
         "category": "concepts", "domain": [], "tags": [], "inbound": 0, "outbound": 0},
        {"id": "delta-tag", "kind": "tag", "title": "delta-tag",
         "type": None, "category": None, "domain": [], "tags": [], "inbound": 1, "outbound": 0},
    ],
    "links": [
        {"source": "beta",  "target": "alpha", "kind": "wikilink"},
        {"source": "gamma", "target": "alpha", "kind": "wikilink"},
        {"source": "alpha", "target": "gamma", "kind": "wikilink"},
    ],
}


@pytest.fixture
def graph_stub():
    return json.loads(json.dumps(GRAPH_STUB))
