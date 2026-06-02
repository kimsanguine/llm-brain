import json
from pathlib import Path

import pytest


_WIKI_ROOT = Path(__file__).parent.parent / "wiki"


def _has_wiki_data(root: Path) -> bool:
    return root.exists() and (root / "concepts").exists() and any((root / "concepts").glob("*.md"))


# 사용자(작성자)의 실제 wiki/ 데이터 존재 여부. wiki/ 는 .gitignore 되어 있어
# CI 러너 또는 fresh clone 환경엔 없다.
_HAS_USER_WIKI = _has_wiki_data(_WIKI_ROOT)


def pytest_configure(config):
    """`requires_user_wiki` 마커 등록 — PytestUnknownMarkWarning 방지.

    pyproject.toml 에 [tool.pytest.ini_options] 섹션이 없으므로 마커를
    여기서 코드로 등록한다 (마커 등록의 정식 메커니즘).
    """
    config.addinivalue_line(
        "markers",
        "requires_user_wiki: 작성자의 실제 wiki/ 데이터(real index.md + 페이지)에 "
        "의존하는 테스트. wiki/ 부재(fresh clone/CI) 시 자동 skip.",
    )


def pytest_collection_modifyitems(config, items):
    """`requires_user_wiki` 마커가 달린 테스트만 사용자 wiki 부재 시 skip.

    기존 구현은 `test_wiki_app_*` 파일을 *파일명 기준*으로 통째 skip 해서,
    같은 파일 안의 self-contained(tmp_path) 테스트까지 fresh clone/CI 에서
    돌지 않는 문제가 있었다. 이제는 실제 사용자 wiki 데이터를 가정하는
    개별 테스트만 마커를 달고, 마커 없는 self-contained 테스트는 wiki 유무와
    무관하게 항상 실행한다.
    """
    if _HAS_USER_WIKI:
        return
    skip = pytest.mark.skip(reason="requires user wiki data (wiki/ is gitignored)")
    for item in items:
        if item.get_closest_marker("requires_user_wiki") is not None:
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
