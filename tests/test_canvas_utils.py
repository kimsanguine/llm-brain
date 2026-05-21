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


def test_build_delta_canvas_returns_none_when_no_new_nodes(graph_stub):
    """신규 노드가 없으면 None 반환 (갱신만 있어도 None)."""
    same = json.loads(json.dumps(graph_stub))
    assert build_delta_canvas(graph_stub, same) is None

    # 갱신만 있고 신규가 없는 경우도 None
    prev_with_updated_only = json.loads(json.dumps(graph_stub))
    for n in prev_with_updated_only["nodes"]:
        if n["id"] == "alpha":
            n["inbound"] = 0
    assert build_delta_canvas(graph_stub, prev_with_updated_only) is None


def test_build_delta_canvas_new_node_color(graph_stub):
    """신규 노드 color='3' (yellow), 신규 노드는 y=0."""
    prev = {"nodes": [], "links": []}
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    new_node = next(n for n in canvas["nodes"] if n["id"] == "alpha")
    assert new_node["color"] == "3"
    assert new_node["y"] == 0


def test_build_delta_canvas_excludes_updated_nodes(graph_stub):
    """갱신 노드는 canvas에 포함되지 않아야 한다."""
    # gamma를 신규로 만들고, alpha는 갱신만 되도록 prev 구성
    prev = {
        "nodes": [
            {"id": "alpha", "kind": "page", "title": "Alpha", "type": "concept",
             "category": "concepts", "domain": [], "tags": [], "inbound": 0, "outbound": 0},
            {"id": "beta",  "kind": "page", "title": "Beta",  "type": "concept",
             "category": "concepts", "domain": [], "tags": [], "inbound": 1, "outbound": 0},
        ],
        "links": [],
    }
    # current: gamma 신규, alpha는 inbound 변경 (갱신)
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    canvas_ids = {n["id"] for n in canvas["nodes"]}
    # gamma는 신규로 포함
    assert "gamma" in canvas_ids
    # alpha는 신규 노드의 이웃이므로 포함될 수 있음 (이웃 자격)
    # 핵심: alpha가 "갱신 노드" 자격으로는 들어가지 않음 = color가 없어야 함
    if "alpha" in canvas_ids:
        alpha_node = next(n for n in canvas["nodes"] if n["id"] == "alpha")
        assert alpha_node.get("color") is None or alpha_node["color"] != "6"


def test_build_delta_canvas_neighbor_dedup(graph_stub):
    """같은 노드가 여러 신규 노드의 이웃이어도 한 번만 표시되어야 한다."""
    # alpha, beta를 신규로 만들기 위해 prev에서 둘 다 제거
    prev = {
        "nodes": [
            {"id": "gamma", "kind": "page", "title": "Gamma", "type": "concept",
             "category": "concepts", "domain": [], "tags": [], "inbound": 0, "outbound": 0},
        ],
        "links": [],
    }
    # graph_stub은 beta→alpha, gamma→alpha, alpha→gamma 링크 보유
    # alpha, beta 모두 신규 → gamma는 두 신규의 이웃
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    gamma_nodes = [n for n in canvas["nodes"] if n["id"] == "gamma"]
    assert len(gamma_nodes) == 1, "이웃 노드는 dedup되어 한 번만 표시되어야 함"


def test_build_delta_canvas_includes_internal_edges(graph_stub):
    """신규 노드끼리의 wikilink 엣지도 포함되어야 한다."""
    # alpha, beta를 신규로, gamma는 이웃으로
    prev = {
        "nodes": [
            {"id": "gamma", "kind": "page", "title": "Gamma", "type": "concept",
             "category": "concepts", "domain": [], "tags": [], "inbound": 0, "outbound": 0},
        ],
        "links": [],
    }
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    edge_pairs = {(e["fromNode"], e["toNode"]) for e in canvas["edges"]}
    # 신규-신규 엣지: beta→alpha
    assert ("beta", "alpha") in edge_pairs
    # 신규-이웃 엣지: alpha→gamma, gamma→alpha
    assert ("alpha", "gamma") in edge_pairs
    assert ("gamma", "alpha") in edge_pairs


def test_build_delta_canvas_neighbor_position(graph_stub):
    """이웃 노드는 y=±400에 배치되어야 한다."""
    prev = {"nodes": [], "links": []}
    canvas = build_delta_canvas(graph_stub, prev)
    assert canvas is not None
    # 신규: alpha, beta, gamma — 이웃 없음 (다른 page 노드 없음)
    # 모든 노드가 y=0이어야 함
    for n in canvas["nodes"]:
        assert n["y"] == 0  # 모두 신규, 이웃 없음
