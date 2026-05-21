import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from canvas_utils import build_neighborhood_canvas, save_canvas


# ── Neighborhood canvas ────────────────────────────────────────────────

def test_neighborhood_center_node(graph_stub):
    """중앙 노드가 color='4', x=0, y=0으로 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    nodes = {n["id"]: n for n in canvas["nodes"]}
    assert "alpha" in nodes
    assert nodes["alpha"]["color"] == "4"
    assert nodes["alpha"]["x"] == 0
    assert nodes["alpha"]["y"] == 0


def test_neighborhood_inbound_nodes(graph_stub):
    """inbound 노드들이 x=-340에 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    inbound_ids = {n["id"] for n in canvas["nodes"] if n.get("x") == -340}
    assert "beta" in inbound_ids
    assert "gamma" in inbound_ids


def test_neighborhood_outbound_nodes(graph_stub):
    """outbound 노드들이 x=+340에 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    outbound_ids = {n["id"] for n in canvas["nodes"] if n.get("x") == 340}
    assert "gamma" in outbound_ids


def test_neighborhood_edges(graph_stub):
    """edges가 inbound→center, center→outbound 방향으로 생성되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    edge_pairs = {(e["fromNode"], e["toNode"]) for e in canvas["edges"]}
    assert ("beta", "alpha") in edge_pairs
    assert ("alpha", "gamma") in edge_pairs


def test_neighborhood_max_5_inbound(graph_stub):
    """inbound 노드가 5개를 초과하면 상위 5개만 포함."""
    for i in range(6):
        node_id = f"in{i}"
        graph_stub["nodes"].append({
            "id": node_id, "kind": "page", "title": node_id,
            "type": "concept", "category": "concepts", "domain": [], "tags": [],
            "inbound": i, "outbound": 0,
        })
        graph_stub["links"].append({"source": node_id, "target": "alpha", "kind": "wikilink"})
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    inbound_nodes = [n for n in canvas["nodes"] if n.get("x") == -340]
    assert len(inbound_nodes) <= 5


def test_save_canvas(graph_stub, tmp_path):
    """save_canvas가 JSON 파일을 올바르게 저장해야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    out = tmp_path / "test.canvas"
    save_canvas(canvas, out)
    loaded = json.loads(out.read_text())
    assert "nodes" in loaded
    assert "edges" in loaded


def test_neighborhood_missing_slug(graph_stub):
    """graph에 없는 slug면 None을 반환해야 한다."""
    result = build_neighborhood_canvas(graph_stub, "nonexistent-slug")
    assert result is None


def test_neighborhood_tag_nodes_excluded(graph_stub):
    """tag 노드는 center로 지정할 수 없어야 한다."""
    result = build_neighborhood_canvas(graph_stub, "delta-tag")
    assert result is None


# ── Delta canvas ────────────────────────────────────────────

from canvas_utils import compute_delta, build_delta_canvas


def test_compute_delta_new_nodes(graph_stub):
    """prev에 없고 current에 있는 page 노드는 new_nodes에 포함."""
    prev = {"nodes": [], "links": []}
    delta = compute_delta(graph_stub, prev)
    new_ids = {n["id"] for n in delta["new_nodes"]}
    assert "alpha" in new_ids
    assert "beta" in new_ids


def test_compute_delta_removed_nodes(graph_stub):
    """prev에 있고 current에 없는 page 노드는 removed_nodes에 포함."""
    prev = json.loads(json.dumps(graph_stub))
    prev["nodes"].append({
        "id": "old-page", "kind": "page", "title": "Old",
        "type": "concept", "category": "concepts", "domain": [], "tags": [],
        "inbound": 0, "outbound": 0,
    })
    delta = compute_delta(graph_stub, prev)
    assert "old-page" in {n["id"] for n in delta["removed_nodes"]}


def test_compute_delta_excludes_ghost_from_removed(graph_stub):
    """ghost 노드는 removed_nodes에 포함되지 않아야 한다."""
    prev = json.loads(json.dumps(graph_stub))
    prev["nodes"].append({
        "id": "ghost-1", "kind": "ghost", "title": "Ghost",
        "type": None, "category": None, "domain": [], "tags": [],
        "inbound": 0, "outbound": 0,
    })
    delta = compute_delta(graph_stub, prev)
    assert "ghost-1" not in {n["id"] for n in delta["removed_nodes"]}


def test_compute_delta_updated_nodes(graph_stub):
    """inbound count가 변한 노드는 updated_nodes에 포함."""
    prev = json.loads(json.dumps(graph_stub))
    for n in prev["nodes"]:
        if n["id"] == "alpha":
            n["inbound"] = 0
    delta = compute_delta(graph_stub, prev)
    assert "alpha" in {n["id"] for n in delta["updated_nodes"]}


def test_compute_delta_new_edges(graph_stub):
    """prev에 없는 엣지는 new_edges에 포함."""
    prev = {"nodes": list(graph_stub["nodes"]), "links": []}
    delta = compute_delta(graph_stub, prev)
    assert len(delta["new_edges"]) == len(graph_stub["links"])


def test_build_delta_canvas_returns_none_when_no_delta(graph_stub):
    """변경 없으면 None 반환."""
    same = json.loads(json.dumps(graph_stub))
    result = build_delta_canvas(graph_stub, same)
    assert result is None


def test_build_delta_canvas_new_node_color(graph_stub):
    """신규 노드 color='3' (yellow)."""
    prev = {"nodes": [], "links": []}
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    new_node = next(n for n in canvas["nodes"] if n["id"] == "alpha")
    assert new_node["color"] == "3"


def test_build_delta_canvas_updated_node_color(graph_stub):
    """갱신 노드 color='6' (purple)."""
    prev = json.loads(json.dumps(graph_stub))
    for n in prev["nodes"]:
        if n["id"] == "alpha":
            n["inbound"] = 0
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    upd_node = next((n for n in canvas["nodes"] if n["id"] == "alpha"), None)
    assert upd_node is not None
    assert upd_node["color"] == "6"
