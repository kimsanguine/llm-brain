# Graph Delta & Canvas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/ingest` 후 그래프 변경 내역을 터미널·Canvas로 출력하고, `/query` 답변에 대상 노드의 1-depth 네이버후드 Canvas를 생성한다.

**Architecture:** `scripts/canvas_utils.py`를 신규 생성해 Canvas JSON 빌드 로직을 분리하고, `ingest.py`는 스냅샷 비교 + 델타 Canvas 생성을, `curate.py`는 `--graph` 제거 후 품질 관리에 집중한다. 커맨드 파일 3개(.claude/commands/)를 업데이트해 LLM 흐름에 Canvas 단계를 추가한다.

**Tech Stack:** Python 3.11+, pytest, json stdlib, pathlib, `wiki/graph.json` (D3 호환), Obsidian Canvas JSON spec

---

## 파일 구조

| 파일 | 상태 | 역할 |
|------|------|------|
| `scripts/canvas_utils.py` | **신규** | Canvas JSON 빌드 + 저장 유틸 |
| `tests/__init__.py` | **신규** | pytest 패키지 초기화 |
| `tests/conftest.py` | **신규** | 공통 픽스처 (graph stub) |
| `tests/test_canvas_utils.py` | **신규** | canvas_utils 단위 테스트 |
| `tests/test_ingest_delta.py` | **신규** | ingest delta 단위 테스트 |
| `scripts/ingest.py` | **수정** | 스냅샷·delta·canvas 호출 추가 |
| `scripts/curate.py` | **수정** | `--graph` / `run_graph()` 제거 |
| `.claude/commands/ingest.md` | **수정** | delta + canvas 단계 추가 |
| `.claude/commands/curate.md` | **수정** | `--graph` 설명 제거 |
| `.claude/commands/query.md` | **수정** | 연결 요약 + canvas 단계 추가 |
| `pyproject.toml` | **수정** | pytest dev 의존성 추가 |
| `.gitignore` | **수정** | `wiki/.graph_prev.json`, `wiki/canvas/` 추가 |

---

## Task 1: 테스트 인프라 세팅

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: pytest 임시 테스트 작성**

```python
# tests/__init__.py (빈 파일)
```

```python
# tests/conftest.py
import json
import pytest
from pathlib import Path

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
```

```python
# tests/test_infra.py  ← 인프라 검증용, Task 1 완료 후 삭제
def test_pytest_works():
    assert 1 + 1 == 2
```

- [ ] **Step 2: pytest 실행 — FAIL 확인 (모듈 없으므로 오류 또는 1 pass)**

```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run pytest tests/test_infra.py -v
```

Expected: `1 passed` (pytest가 설치되지 않으면 `ModuleNotFoundError: pytest`)

- [ ] **Step 3: pyproject.toml dev 의존성 추가**

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

- [ ] **Step 4: uv sync**

```bash
uv sync
```

Expected: `Resolved ... packages` (pytest 설치됨)

- [ ] **Step 5: pytest 재실행 — PASS 확인**

```bash
uv run pytest tests/test_infra.py -v
```

Expected: `1 passed`

- [ ] **Step 6: tests/test_infra.py 삭제 후 커밋**

```bash
rm tests/test_infra.py
git add pyproject.toml tests/__init__.py tests/conftest.py
git commit -m "chore: add pytest dev dep + test fixtures"
```

---

## Task 2: canvas_utils.py — neighborhood canvas (TDD)

**Files:**
- Create: `scripts/canvas_utils.py`
- Create: `tests/test_canvas_utils.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/test_canvas_utils.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import json
import pytest
from canvas_utils import build_neighborhood_canvas, save_canvas


def test_neighborhood_center_node(graph_stub, tmp_path):
    """중앙 노드가 color='4', x=0, y=0으로 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    nodes = {n["id"]: n for n in canvas["nodes"]}
    assert "alpha" in nodes
    assert nodes["alpha"]["color"] == "4"
    assert nodes["alpha"]["x"] == 0
    assert nodes["alpha"]["y"] == 0


def test_neighborhood_inbound_nodes(graph_stub, tmp_path):
    """inbound 노드들이 x=-340에 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    nodes = {n["id"]: n for n in canvas["nodes"]}
    # beta, gamma → alpha (inbound of alpha)
    inbound_ids = {n["id"] for n in canvas["nodes"] if n.get("x") == -340}
    assert "beta" in inbound_ids
    assert "gamma" in inbound_ids


def test_neighborhood_outbound_nodes(graph_stub, tmp_path):
    """outbound 노드들이 x=+340에 배치되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    nodes = {n["id"]: n for n in canvas["nodes"]}
    outbound_ids = {n["id"] for n in canvas["nodes"] if n.get("x") == 340}
    # alpha → gamma (outbound of alpha)
    assert "gamma" in outbound_ids


def test_neighborhood_edges(graph_stub):
    """edges가 inbound→center, center→outbound 방향으로 생성되어야 한다."""
    canvas = build_neighborhood_canvas(graph_stub, "alpha")
    edge_pairs = {(e["fromNode"], e["toNode"]) for e in canvas["edges"]}
    assert ("beta", "alpha") in edge_pairs    # inbound edge
    assert ("alpha", "gamma") in edge_pairs   # outbound edge


def test_neighborhood_max_5_inbound(graph_stub):
    """inbound 노드가 5개를 초과하면 inbound_count 내림차순 상위 5개만 포함."""
    # graph_stub에 inbound 노드 6개 추가
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
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_canvas_utils.py -v
```

Expected: `ImportError: cannot import name 'build_neighborhood_canvas'`

- [ ] **Step 3: canvas_utils.py 구현 (neighborhood 부분)**

```python
# scripts/canvas_utils.py
"""
canvas_utils.py — Obsidian Canvas JSON 생성 유틸

공개 API:
  build_neighborhood_canvas(graph_data, slug) -> dict | None
  build_delta_canvas(current_graph, prev_graph) -> dict | None
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

# Obsidian Canvas color: 1=red 2=orange 3=yellow 4=green 5=cyan 6=purple
_COLOR_QUERY_CENTER = "4"   # green — 현재 쿼리 노드
_COLOR_NEW_NODE     = "3"   # yellow — ingest 신규 노드
_COLOR_UPDATED_NODE = "6"   # purple — ingest 갱신 노드
_DELTA_X_SPACING    = 320


def _wiki_path(node: dict) -> str:
    """graph 노드에서 wiki 파일 경로를 반환한다."""
    category = node.get("category") or "concepts"
    return f"wiki/{category}/{node['id']}.md"


def _make_file_node(node_id: str, wiki_path: str, x: int, y: int,
                    color: str | None = None,
                    w: int = 250, h: int = 60) -> dict:
    n = {
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


def build_neighborhood_canvas(graph_data: dict, slug: str) -> dict | None:
    """
    slug 노드의 1-depth 네이버후드 Canvas를 반환한다.

    inbound/outbound 각 최대 5개, inbound_count 내림차순.
    slug가 graph에 없으면 None 반환.
    """
    nodes_by_id = {n["id"]: n for n in graph_data["nodes"] if n["kind"] == "page"}
    if slug not in nodes_by_id:
        return None

    links = graph_data.get("links", [])
    center_node = nodes_by_id[slug]

    # inbound: links where target == slug, page 노드만
    inbound_ids = [
        lnk["source"] for lnk in links
        if lnk["target"] == slug and lnk["source"] in nodes_by_id
    ]
    # outbound: links where source == slug, page 노드만
    outbound_ids = [
        lnk["target"] for lnk in links
        if lnk["source"] == slug and lnk["target"] in nodes_by_id
    ]

    # 상위 5개 — inbound_count 내림차순
    def _sort_key(nid: str) -> int:
        return nodes_by_id[nid].get("inbound", 0)

    inbound_ids = sorted(set(inbound_ids), key=_sort_key, reverse=True)[:_MAX_NEIGHBORS]
    outbound_ids = sorted(set(outbound_ids), key=_sort_key, reverse=True)[:_MAX_NEIGHBORS]

    canvas_nodes = []
    canvas_edges = []

    # 중앙 노드
    canvas_nodes.append(_make_file_node(
        slug, _wiki_path(center_node),
        _CENTER_X, _CENTER_Y, _COLOR_QUERY_CENTER,
        w=_CENTER_W, h=_CENTER_H,
    ))

    # inbound 노드 (왼쪽)
    for i, nid in enumerate(inbound_ids):
        y = (i - len(inbound_ids) // 2) * _SIDE_Y_SPACING
        canvas_nodes.append(_make_file_node(
            nid, _wiki_path(nodes_by_id[nid]),
            -_SIDE_X_OFFSET, y,
        ))
        canvas_edges.append(_make_edge(f"e-in-{i}", nid, slug))

    # outbound 노드 (오른쪽)
    for i, nid in enumerate(outbound_ids):
        y = (i - len(outbound_ids) // 2) * _SIDE_Y_SPACING
        canvas_nodes.append(_make_file_node(
            nid, _wiki_path(nodes_by_id[nid]),
            _SIDE_X_OFFSET, y,
        ))
        canvas_edges.append(_make_edge(f"e-out-{i}", slug, nid))

    return {"nodes": canvas_nodes, "edges": canvas_edges}


def save_canvas(canvas_data: dict, path: Path) -> None:
    """canvas_data를 Obsidian Canvas JSON 파일로 저장한다."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canvas_data, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: 테스트 재실행 — PASS 확인**

```bash
uv run pytest tests/test_canvas_utils.py -v -k "neighborhood"
```

Expected: `6 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/canvas_utils.py tests/test_canvas_utils.py tests/__init__.py tests/conftest.py
git commit -m "feat: canvas_utils — neighborhood canvas builder (TDD)"
```

---

## Task 3: canvas_utils.py — delta canvas (TDD)

**Files:**
- Modify: `scripts/canvas_utils.py`
- Modify: `tests/test_canvas_utils.py`

- [ ] **Step 1: delta 테스트 추가**

`tests/test_canvas_utils.py` 파일 하단에 다음을 추가:

```python
from canvas_utils import compute_delta, build_delta_canvas


def test_compute_delta_new_nodes(graph_stub):
    """prev에 없고 current에 있는 page 노드는 new_nodes에 포함."""
    prev = {"nodes": [], "links": []}
    delta = compute_delta(graph_stub, prev)
    assert "alpha" in {n["id"] for n in delta["new_nodes"]}
    assert "beta"  in {n["id"] for n in delta["new_nodes"]}


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
    # alpha의 inbound를 0으로 바꿔 prev에 넣기
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
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_canvas_utils.py -v -k "delta"
```

Expected: `ImportError: cannot import name 'compute_delta'`

- [ ] **Step 3: canvas_utils.py에 delta 함수 추가**

`scripts/canvas_utils.py` 파일 끝에 다음을 추가 (기존 코드 유지):

```python
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
    new_edges = [
        {"source": s, "target": t} for s, t in cur_edges - prv_edges
    ]

    return {
        "new_nodes":     new_nodes,
        "removed_nodes": removed_nodes,
        "updated_nodes": updated_nodes,
        "new_edges":     new_edges,
    }


def build_delta_canvas(current: dict, prev: dict) -> dict | None:
    """
    ingest delta를 시각화한 Canvas를 반환한다.
    delta가 없으면 None 반환.

    노드 배치:
      - 신규/갱신 노드: 중앙 행에 x 간격 _DELTA_X_SPACING px
      - 신규 노드의 inbound: 왼쪽 열 (x = 첫 delta node x - _SIDE_X_OFFSET)
      - 신규 노드의 outbound: 오른쪽 열
    """
    delta = compute_delta(current, prev)
    delta_nodes = delta["new_nodes"] + delta["updated_nodes"]
    if not delta_nodes:
        return None

    cur_nodes_by_id = {n["id"]: n for n in current["nodes"] if n["kind"] == "page"}
    links = current.get("links", [])

    canvas_nodes: list[dict] = []
    canvas_edges: list[dict] = []

    for col_idx, node in enumerate(delta_nodes):
        color = _COLOR_NEW_NODE if node in delta["new_nodes"] else _COLOR_UPDATED_NODE
        cx = col_idx * _DELTA_X_SPACING
        cy = 0

        canvas_nodes.append(_make_file_node(
            node["id"], _wiki_path(node),
            cx, cy, color,
        ))

        # inbound 맥락 노드 (최대 5개)
        inbound_ids = [
            lnk["source"] for lnk in links
            if lnk["target"] == node["id"] and lnk["source"] in cur_nodes_by_id
        ]
        inbound_ids = sorted(set(inbound_ids),
                             key=lambda nid: cur_nodes_by_id[nid].get("inbound", 0),
                             reverse=True)[:_MAX_NEIGHBORS]

        for i, nid in enumerate(inbound_ids):
            ctx_id = f"ctx-in-{col_idx}-{i}"
            y = (i - len(inbound_ids) // 2) * _SIDE_Y_SPACING
            canvas_nodes.append(_make_file_node(
                ctx_id, _wiki_path(cur_nodes_by_id[nid]),
                cx - _SIDE_X_OFFSET, y,
            ))
            canvas_edges.append(_make_edge(f"e-in-{col_idx}-{i}", ctx_id, node["id"]))

        # outbound 맥락 노드 (최대 5개)
        outbound_ids = [
            lnk["target"] for lnk in links
            if lnk["source"] == node["id"] and lnk["target"] in cur_nodes_by_id
        ]
        outbound_ids = sorted(set(outbound_ids),
                              key=lambda nid: cur_nodes_by_id[nid].get("inbound", 0),
                              reverse=True)[:_MAX_NEIGHBORS]

        for i, nid in enumerate(outbound_ids):
            ctx_id = f"ctx-out-{col_idx}-{i}"
            y = (i - len(outbound_ids) // 2) * _SIDE_Y_SPACING
            canvas_nodes.append(_make_file_node(
                ctx_id, _wiki_path(cur_nodes_by_id[nid]),
                cx + _SIDE_X_OFFSET, y,
            ))
            canvas_edges.append(_make_edge(f"e-out-{col_idx}-{i}", node["id"], ctx_id))

    return {"nodes": canvas_nodes, "edges": canvas_edges}
```

- [ ] **Step 4: 테스트 재실행 — PASS 확인**

```bash
uv run pytest tests/test_canvas_utils.py -v
```

Expected: `전체 PASS` (neighborhood + delta 합계 ~15개)

- [ ] **Step 5: 커밋**

```bash
git add scripts/canvas_utils.py tests/test_canvas_utils.py
git commit -m "feat: canvas_utils — delta canvas + compute_delta (TDD)"
```

---

## Task 4: ingest.py — 스냅샷 + delta 통합

**Files:**
- Modify: `scripts/ingest.py`
- Create: `tests/test_ingest_delta.py`

- [ ] **Step 1: ingest delta 테스트 작성**

```python
# tests/test_ingest_delta.py
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from ingest import snapshot_graph, run_delta_pipeline


@pytest.fixture
def tmp_wiki(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    return wiki_dir


def test_snapshot_graph_copies_file(tmp_wiki):
    """graph.json이 있으면 .graph_prev.json으로 복사해야 한다."""
    graph = {"nodes": [], "links": []}
    graph_path = tmp_wiki / "graph.json"
    graph_path.write_text(json.dumps(graph))

    prev_path = tmp_wiki / ".graph_prev.json"
    snapshot_graph(tmp_wiki)
    assert prev_path.exists()
    assert json.loads(prev_path.read_text()) == graph


def test_snapshot_graph_no_op_when_missing(tmp_wiki):
    """graph.json이 없으면 오류 없이 종료해야 한다."""
    snapshot_graph(tmp_wiki)  # should not raise
    assert not (tmp_wiki / ".graph_prev.json").exists()


def test_run_delta_pipeline_first_run(tmp_wiki, graph_stub):
    """
    .graph_prev.json이 없고 graph.json이 있으면
    전체 page 노드를 신규로 취급해야 한다.
    """
    (tmp_wiki / "graph.json").write_text(
        json.dumps(graph_stub)
    )
    result = run_delta_pipeline(tmp_wiki)
    assert result is not None
    new_ids = {n["id"] for n in result["new_nodes"]}
    assert "alpha" in new_ids
    assert "beta"  in new_ids


def test_run_delta_pipeline_no_change(tmp_wiki, graph_stub):
    """prev == current이면 None을 반환해야 한다."""
    same = json.dumps(graph_stub)
    (tmp_wiki / "graph.json").write_text(same)
    (tmp_wiki / ".graph_prev.json").write_text(same)
    result = run_delta_pipeline(tmp_wiki)
    assert result is None
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_ingest_delta.py -v
```

Expected: `ImportError: cannot import name 'snapshot_graph'`

- [ ] **Step 3: ingest.py에 snapshot + delta 함수 추가**

`scripts/ingest.py`의 import 블록에 다음을 추가 (기존 import 뒤에):

```python
import subprocess
```

파일 끝 (`if __name__ == "__main__":` 바로 위)에 다음 함수들을 추가:

```python
# ── Graph delta pipeline ────────────────────────────────────

GRAPH_FILE = WIKI_ROOT / "wiki" / "graph.json"
GRAPH_PREV_FILE = WIKI_ROOT / "wiki" / ".graph_prev.json"
CANVAS_DIR = WIKI_ROOT / "wiki" / "canvas"
EXPORT_SCRIPT = Path(__file__).parent / "export_graph.py"


def snapshot_graph(wiki_dir: Path | None = None) -> None:
    """wiki/graph.json → wiki/.graph_prev.json 복사. graph.json 없으면 무시."""
    src = (wiki_dir or WIKI_ROOT / "wiki") / "graph.json"
    dst = (wiki_dir or WIKI_ROOT / "wiki") / ".graph_prev.json"
    if src.exists():
        import shutil as _shutil
        _shutil.copy2(src, dst)


def run_delta_pipeline(wiki_dir: Path | None = None) -> dict | None:
    """
    현재 graph.json과 .graph_prev.json을 비교해 delta dict를 반환한다.
    delta가 없거나 graph.json이 없으면 None 반환.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from canvas_utils import compute_delta

    _wiki = wiki_dir or WIKI_ROOT / "wiki"
    cur_path  = _wiki / "graph.json"
    prev_path = _wiki / ".graph_prev.json"

    if not cur_path.exists():
        return None

    current = json.loads(cur_path.read_text())
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else {"nodes": [], "links": []}

    delta = compute_delta(current, prev)
    has_changes = any([
        delta["new_nodes"], delta["removed_nodes"],
        delta["updated_nodes"], delta["new_edges"],
    ])
    return delta if has_changes else None


def print_delta(delta: dict) -> None:
    """delta를 터미널에 출력한다."""
    n_new  = len(delta["new_nodes"])
    n_upd  = len(delta["updated_nodes"])
    n_rem  = len(delta["removed_nodes"])
    print(f"[ingest] delta — {n_new}개 신규, {n_upd}개 갱신, {n_rem}개 제거")

    for node in delta["new_nodes"]:
        cat = node.get("category", "?")
        print(f"  + {node['id']}  ({cat}/)  inbound 0 → {node['inbound']}")

    for node in delta["updated_nodes"]:
        cat = node.get("category", "?")
        print(f"  ~ {node['id']}  ({cat}/)  inbound 변경 → {node['inbound']}")

    for node in delta["removed_nodes"]:
        cat = node.get("category", "?")
        print(f"  - {node['id']}  ({cat}/)  제거됨")

    new_edges = delta["new_edges"]
    if new_edges:
        first = new_edges[0]
        rest  = len(new_edges) - 1
        msg = f"  엣지 +{len(new_edges)}: {first['source']} → {first['target']}"
        if rest > 0:
            msg += f" 외 {rest}개"
        print(msg)


def generate_ingest_delta_canvas(wiki_dir: Path | None = None) -> bool:
    """
    delta canvas를 wiki/canvas/ingest-delta.canvas로 저장한다.
    snapshot_graph() + export_graph.py 실행 이후에 호출해야 한다.
    canvas가 생성되면 True, delta 없으면 False 반환.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from canvas_utils import build_delta_canvas, save_canvas

    _wiki = wiki_dir or WIKI_ROOT / "wiki"
    cur_path  = _wiki / "graph.json"
    prev_path = _wiki / ".graph_prev.json"

    if not cur_path.exists():
        return False

    current = json.loads(cur_path.read_text())
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else {"nodes": [], "links": []}

    canvas = build_delta_canvas(current, prev)
    if canvas is None:
        return False

    out_path = _wiki / "canvas" / "ingest-delta.canvas"
    save_canvas(canvas, out_path)
    print(f"[ingest] canvas → wiki/canvas/ingest-delta.canvas")
    return True
```

- [ ] **Step 4: 테스트 재실행 — PASS 확인**

```bash
uv run pytest tests/test_ingest_delta.py -v
```

Expected: `4 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/ingest.py tests/test_ingest_delta.py
git commit -m "feat: ingest — snapshot_graph, run_delta_pipeline, generate_ingest_delta_canvas"
```

---

## Task 5: curate.py — `--graph` 제거

**Files:**
- Modify: `scripts/curate.py`

`--graph` 관련 코드를 외과적으로 제거한다. 아래 변경만 적용하고 나머지 코드는 건드리지 않는다.

- [ ] **Step 1: curate.py 수정 — 3곳 변경**

**변경 1** — `main()` 의 `--graph` 인자 제거 (line ~473):

```python
# 제거 전:
parser.add_argument("--graph", action="store_true", help="wikilink 인바운드 분석 + graph_report.md 생성")

# 제거 후: 해당 줄 삭제
```

**변경 2** — `run_all` 조건 수정 (line ~486):

```python
# 제거 전:
run_all = args.all or not any([args.audit, args.distill, args.lifecycle, args.graph])

# 수정 후:
run_all = args.all or not any([args.audit, args.distill, args.lifecycle])
```

**변경 3** — `graph_result` 변수 및 `write_report` 호출 수정 (line ~493):

```python
# 제거 전:
graph_result = run_graph(pages) if (run_all or args.graph) else None
write_report(audit_result, distilled, lifecycle_result, graph_result)

# 수정 후:
write_report(audit_result, distilled, lifecycle_result)
```

`run_graph()` 함수 본체(line 262~344)도 삭제한다. `GRAPH_REPORT_FILE` 상수도 삭제한다.

- [ ] **Step 2: curate --graph 거부 확인**

```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python scripts/curate.py --graph 2>&1 | head -5
```

Expected: `error: unrecognized arguments: --graph`

- [ ] **Step 3: curate --all 정상 동작 확인**

```bash
uv run python scripts/curate.py --all 2>&1 | tail -5
```

Expected: `[curate] 리포트 저장: wiki/curate_report.md` (graph 섹션 없음)

- [ ] **Step 4: 커밋**

```bash
git add scripts/curate.py
git commit -m "feat: curate — remove --graph flag and run_graph() (graph delta moved to ingest)"
```

---

## Task 6: 커맨드 파일 업데이트

**Files:**
- Modify: `.claude/commands/ingest.md`
- Modify: `.claude/commands/curate.md`
- Modify: `.claude/commands/query.md`

- [ ] **Step 1: ingest.md 업데이트**

`.claude/commands/ingest.md` 파일에서 **Step 3 (완료 표시)** 뒤에 다음 Step 4, Step 5를 추가:

```markdown
## Step 4: 그래프 delta 처리

wiki 컴파일이 완료된 후 아래를 순서대로 실행하세요.

**4-0. 스냅샷 (export_graph.py 실행 전 반드시 먼저)**

```python
import sys
sys.path.insert(0, "scripts")
from ingest import snapshot_graph
snapshot_graph()  # graph.json → .graph_prev.json 복사
```

**4-1. export_graph.py 실행 (graph.json 갱신)**
```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run python scripts/export_graph.py
```

**4-2. delta 계산 및 출력**

Python으로 delta를 계산해 터미널에 출력하세요:

```python
import sys
sys.path.insert(0, "scripts")
from ingest import run_delta_pipeline, print_delta
delta = run_delta_pipeline()
if delta:
    print_delta(delta)
else:
    print("[ingest] delta — 변경 없음")
```

## Step 5: Canvas 생성

delta가 있으면 wiki/canvas/ingest-delta.canvas를 생성하세요:

```python
import sys
sys.path.insert(0, "scripts")
from ingest import generate_ingest_delta_canvas
generated = generate_ingest_delta_canvas()  # delta는 내부에서 graph.json vs .graph_prev.json 비교
if not generated:
    print("[ingest] canvas 생성 생략 (delta 없음)")
```

생성된 canvas 파일은 Obsidian에서 `wiki/canvas/ingest-delta.canvas`를 열어 확인할 수 있습니다.

> **단, wiki 페이지가 0개이거나 delta가 없으면 Step 4~5를 건너뜁니다.**
```

- [ ] **Step 2: curate.md 업데이트**

`.claude/commands/curate.md`에서 `--graph` 관련 항목을 제거한다.

찾아서 제거할 내용 (해당 줄 또는 블록):
- `--graph` 모드 설명
- `--all` 설명 중 "graph 분석 포함" 또는 유사한 서술
- curate 흐름 중 `--graph` 언급

`--all`은 `audit + distill + lifecycle` 세 가지만 실행한다고 명시한다.

- [ ] **Step 3: query.md 업데이트**

`.claude/commands/query.md`에서 **access_count 기록 단계 뒤**에 다음을 추가:

```markdown
## Step 4: 연결 요약 출력

답변에 사용된 primary 페이지(첫 번째 참조 페이지)에 대해 연결 요약을 출력하세요.

`wiki/graph.json`이 없으면 이 단계를 건너뜁니다.

```python
import sys, json
from pathlib import Path
sys.path.insert(0, "scripts")
from canvas_utils import build_neighborhood_canvas, save_canvas

graph_path = Path("wiki/graph.json")
if graph_path.exists():
    graph = json.loads(graph_path.read_text())
    nodes_by_id = {n["id"]: n for n in graph["nodes"] if n["kind"] == "page"}
    links = graph["links"]

    # primary_slug = 답변에서 참조한 첫 번째 페이지의 slug
    if primary_slug in nodes_by_id:
        node = nodes_by_id[primary_slug]
        inbound_list  = [l["source"] for l in links if l["target"] == primary_slug][:2]
        outbound_list = [l["target"] for l in links if l["source"] == primary_slug][:2]
        n_in  = node["inbound"]
        n_out = node["outbound"]
        print(f"[query] 참조: [[{primary_slug}]]  인바운드 {n_in} / 아웃바운드 {n_out}")
        if inbound_list:
            extra = f" 외 {n_in-2}개" if n_in > 2 else ""
            print(f"  ◀ inbound:  {', '.join(inbound_list)}{extra}")
        if outbound_list:
            extra = f" 외 {n_out-2}개" if n_out > 2 else ""
            print(f"  ▶ outbound: {', '.join(outbound_list)}{extra}")
```

## Step 5: Neighborhood Canvas 생성

primary 페이지의 neighborhood canvas를 생성하세요:

```python
canvas = build_neighborhood_canvas(graph, primary_slug)
if canvas:
    canvas_path = Path(f"wiki/canvas/query-{primary_slug}.canvas")
    save_canvas(canvas, canvas_path)
    print(f"[query] canvas → wiki/canvas/query-{primary_slug}.canvas")
```

graph.json이 없거나 primary 페이지가 graph에 없으면 이 단계를 건너뜁니다.
```

- [ ] **Step 4: 커밋**

```bash
git add .claude/commands/ingest.md .claude/commands/curate.md .claude/commands/query.md
git commit -m "feat: commands — ingest delta+canvas steps, curate --graph removal, query neighborhood"
```

---

## Task 7: .gitignore 업데이트 + 최종 push

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: .gitignore에 항목 추가**

`.gitignore` 파일에 다음을 추가 (기존 `wiki/` 항목 아래):

```
wiki/.graph_prev.json
wiki/canvas/
```

- [ ] **Step 2: 전체 테스트 실행 — 모두 PASS 확인**

```bash
cd /Users/sanguinekim/Documents/3_Code/Vibe/Project/260516_llm_brain
uv run pytest tests/ -v
```

Expected: 전체 통과

- [ ] **Step 3: 커밋**

```bash
git add .gitignore
git commit -m "chore: gitignore — wiki/.graph_prev.json, wiki/canvas/"
```

- [ ] **Step 4: GitHub push**

```bash
git push origin main
```

Expected: `Branch 'main' set up to track remote branch 'main' from 'origin'.`

---

## 검증 체크리스트

| 기능 | 검증 명령 |
|------|----------|
| delta 터미널 출력 | `/ingest <URL>` 후 `[ingest] delta — N개 신규` 출력 확인 |
| ingest-delta.canvas | Obsidian에서 `wiki/canvas/ingest-delta.canvas` 열기 |
| curate --graph 제거 | `uv run python scripts/curate.py --graph` → unrecognized arguments 오류 |
| query canvas | `/query <질문>` 후 `wiki/canvas/query-*.canvas` 생성 확인 |
| 변경 없을 때 | delta 없는 재실행 시 `[ingest] delta — 변경 없음` 출력 |
