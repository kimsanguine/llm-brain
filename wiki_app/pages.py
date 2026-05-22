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
    for cat in _CATEGORIES:
        candidate = wiki_root / cat / f"{slug}.md"
        if candidate.exists():
            return candidate
    raise PageNotFound(f"slug not found: {slug}")


def _load_graph(wiki_root: Path) -> dict:
    """graph.json을 로드하고 slug → node 매핑을 만든다."""
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
        "category": path.relative_to(wiki_root).parts[0],
        "frontmatter": post.metadata,
        "body_md": post.content,
        "inbound": node.get("inbound", 0),
        "outbound": node.get("outbound", 0),
    }
