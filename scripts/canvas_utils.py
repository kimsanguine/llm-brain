"""
canvas_utils.py — Obsidian Canvas JSON 생성 유틸

공개 API:
  build_neighborhood_canvas(graph_data, slug) -> dict | None
  build_delta_canvas(current_graph, prev_graph) -> dict | None
  compute_delta(current, prev) -> dict
  save_canvas(canvas_data, path)
"""
import json
from pathlib import Path


# ── 레이아웃 상수 ────────────────────────────────────────────
_CENTER_X = 0
_CENTER_Y = 0
_CENTER_W = 300
_CENTER_H = 80
_SIDE_X_OFFSET = 340
_SIDE_Y_SPACING = 120
_MAX_NEIGHBORS = 5
_DELTA_X_SPACING = 320

# Obsidian Canvas color: 1=red 2=orange 3=yellow 4=green 5=cyan 6=purple
_COLOR_QUERY_CENTER = "4"   # green — 현재 쿼리 노드
_COLOR_NEW_NODE     = "3"   # yellow — ingest 신규 노드
_COLOR_UPDATED_NODE = "6"   # purple — ingest 갱신 노드


def _wiki_path(node: dict) -> str:
    """graph 노드에서 wiki 파일 경로를 반환한다."""
    category = node.get("category") or "concepts"
    return f"wiki/{category}/{node['id']}.md"


def _make_file_node(node_id: str, wiki_path: str, x: int, y: int,
                    color: str | None = None,
                    w: int = 250, h: int = 60) -> dict:
    n: dict = {
        "id": node_id,
        "type": "file",
        "file": wiki_path,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
    }
    if color:
        n["color"] = color
    return n


def _make_edge(edge_id: str, from_node: str, to_node: str) -> dict:
    return {
        "id": edge_id,
        "fromNode": from_node,
        "toNode": to_node,
        "fromSide": "right",
        "toSide": "left",
    }


# ── Neighborhood canvas ──────────────────────────────────────

def build_neighborhood_canvas(graph_data: dict, slug: str) -> dict | None:
    """
    slug 노드의 1-depth 네이버후드 Canvas를 반환한다.

    inbound/outbound 각 최대 5개, inbound_count 내림차순.
    slug가 page 노드로 graph에 없으면 None 반환.
    """
    nodes_by_id = {n["id"]: n for n in graph_data["nodes"] if n["kind"] == "page"}
    if slug not in nodes_by_id:
        return None

    links = graph_data.get("links", [])
    center_node = nodes_by_id[slug]

    inbound_ids = [
        lnk["source"] for lnk in links
        if lnk["target"] == slug and lnk["source"] in nodes_by_id
    ]
    outbound_ids = [
        lnk["target"] for lnk in links
        if lnk["source"] == slug and lnk["target"] in nodes_by_id
    ]

    def _sort_key(nid: str) -> int:
        return nodes_by_id[nid].get("inbound", 0)

    inbound_ids  = sorted(set(inbound_ids),  key=_sort_key, reverse=True)[:_MAX_NEIGHBORS]
    outbound_ids = sorted(set(outbound_ids), key=_sort_key, reverse=True)[:_MAX_NEIGHBORS]

    canvas_nodes: list[dict] = []
    canvas_edges: list[dict] = []

    canvas_nodes.append(_make_file_node(
        slug, _wiki_path(center_node),
        _CENTER_X, _CENTER_Y, _COLOR_QUERY_CENTER,
        w=_CENTER_W, h=_CENTER_H,
    ))

    for i, nid in enumerate(inbound_ids):
        y = (i - len(inbound_ids) // 2) * _SIDE_Y_SPACING
        canvas_nodes.append(_make_file_node(
            nid, _wiki_path(nodes_by_id[nid]),
            -_SIDE_X_OFFSET, y,
        ))
        canvas_edges.append(_make_edge(f"e-in-{i}", nid, slug))

    for i, nid in enumerate(outbound_ids):
        y = (i - len(outbound_ids) // 2) * _SIDE_Y_SPACING
        canvas_nodes.append(_make_file_node(
            nid, _wiki_path(nodes_by_id[nid]),
            _SIDE_X_OFFSET, y,
        ))
        canvas_edges.append(_make_edge(f"e-out-{i}", slug, nid))

    return {"nodes": canvas_nodes, "edges": canvas_edges}


# ── Delta canvas ────────────────────────────────────────────

def compute_delta(current: dict, prev: dict) -> dict:
    """
    두 graph_data를 비교해 delta를 반환한다.

    반환값:
      new_nodes:     prev에 없고 current에 있는 page 노드
      removed_nodes: current에 없고 prev에 있는 page 노드 (ghost 제외)
      updated_nodes: 두 그래프 모두 존재하며 inbound count가 변경된 page 노드
      new_edges:     prev에 없는 (source, target) 쌍
    """
    cur_pages = {n["id"]: n for n in current["nodes"] if n["kind"] == "page"}
    prv_pages = {n["id"]: n for n in prev["nodes"]    if n["kind"] == "page"}
    prv_ghosts = {n["id"] for n in prev["nodes"] if n["kind"] == "ghost"}

    new_nodes = [cur_pages[nid] for nid in cur_pages if nid not in prv_pages]
    removed_nodes = [
        prv_pages[nid] for nid in prv_pages
        if nid not in cur_pages and nid not in prv_ghosts
    ]
    updated_nodes = [
        cur_pages[nid] for nid in cur_pages
        if nid in prv_pages and cur_pages[nid]["inbound"] != prv_pages[nid]["inbound"]
    ]

    cur_edges = {(lnk["source"], lnk["target"]) for lnk in current.get("links", [])}
    prv_edges = {(lnk["source"], lnk["target"]) for lnk in prev.get("links", [])}
    new_edges = [{"source": s, "target": t} for s, t in cur_edges - prv_edges]

    return {
        "new_nodes":     new_nodes,
        "removed_nodes": removed_nodes,
        "updated_nodes": updated_nodes,
        "new_edges":     new_edges,
    }


def build_delta_canvas(current: dict, prev: dict) -> dict | None:
    """
    ingest delta를 시각화한 Canvas를 반환한다.
    delta(신규 + 갱신 노드)가 없으면 None 반환.

    신규/갱신 노드를 중앙 행에 배치하고
    각 노드의 inbound/outbound 맥락 노드를 좌우에 표시한다.
    """
    delta = compute_delta(current, prev)
    delta_nodes = delta["new_nodes"] + delta["updated_nodes"]
    if not delta_nodes:
        return None

    cur_nodes_by_id = {n["id"]: n for n in current["nodes"] if n["kind"] == "page"}
    links = current.get("links", [])

    canvas_nodes: list[dict] = []
    canvas_edges: list[dict] = []
    new_node_ids = {n["id"] for n in delta["new_nodes"]}

    for col_idx, node in enumerate(delta_nodes):
        color = _COLOR_NEW_NODE if node["id"] in new_node_ids else _COLOR_UPDATED_NODE
        cx = col_idx * _DELTA_X_SPACING

        canvas_nodes.append(_make_file_node(
            node["id"], _wiki_path(node), cx, 0, color,
        ))

        inbound_ids = [
            lnk["source"] for lnk in links
            if lnk["target"] == node["id"] and lnk["source"] in cur_nodes_by_id
        ]
        inbound_ids = sorted(
            set(inbound_ids),
            key=lambda nid: cur_nodes_by_id[nid].get("inbound", 0),
            reverse=True,
        )[:_MAX_NEIGHBORS]

        for i, nid in enumerate(inbound_ids):
            ctx_id = f"ctx-in-{col_idx}-{i}"
            y = (i - len(inbound_ids) // 2) * _SIDE_Y_SPACING
            canvas_nodes.append(_make_file_node(
                ctx_id, _wiki_path(cur_nodes_by_id[nid]),
                cx - _SIDE_X_OFFSET, y,
            ))
            canvas_edges.append(_make_edge(f"e-in-{col_idx}-{i}", ctx_id, node["id"]))

        outbound_ids = [
            lnk["target"] for lnk in links
            if lnk["source"] == node["id"] and lnk["target"] in cur_nodes_by_id
        ]
        outbound_ids = sorted(
            set(outbound_ids),
            key=lambda nid: cur_nodes_by_id[nid].get("inbound", 0),
            reverse=True,
        )[:_MAX_NEIGHBORS]

        for i, nid in enumerate(outbound_ids):
            ctx_id = f"ctx-out-{col_idx}-{i}"
            y = (i - len(outbound_ids) // 2) * _SIDE_Y_SPACING
            canvas_nodes.append(_make_file_node(
                ctx_id, _wiki_path(cur_nodes_by_id[nid]),
                cx + _SIDE_X_OFFSET, y,
            ))
            canvas_edges.append(_make_edge(f"e-out-{col_idx}-{i}", node["id"], ctx_id))

    return {"nodes": canvas_nodes, "edges": canvas_edges}


# ── I/O ─────────────────────────────────────────────────────

def save_canvas(canvas_data: dict, path: Path) -> None:
    """canvas_data를 Obsidian Canvas JSON 파일로 저장한다."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canvas_data, ensure_ascii=False, indent=2))
