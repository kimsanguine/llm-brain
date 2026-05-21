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
    (tmp_wiki / "graph.json").write_text(json.dumps(graph))

    snapshot_graph(tmp_wiki)
    prev_path = tmp_wiki / ".graph_prev.json"
    assert prev_path.exists()
    assert json.loads(prev_path.read_text()) == graph


def test_snapshot_graph_no_op_when_missing(tmp_wiki):
    """graph.json이 없으면 오류 없이 종료해야 한다."""
    snapshot_graph(tmp_wiki)
    assert not (tmp_wiki / ".graph_prev.json").exists()


def test_run_delta_pipeline_first_run(tmp_wiki, graph_stub):
    """
    .graph_prev.json이 없고 graph.json이 있으면
    전체 page 노드를 신규로 취급해야 한다.
    """
    (tmp_wiki / "graph.json").write_text(json.dumps(graph_stub))
    result = run_delta_pipeline(tmp_wiki)
    assert result is not None
    new_ids = {n["id"] for n in result["new_nodes"]}
    assert "alpha" in new_ids
    assert "beta" in new_ids


def test_run_delta_pipeline_no_change(tmp_wiki, graph_stub):
    """prev == current이면 None을 반환해야 한다."""
    same = json.dumps(graph_stub)
    (tmp_wiki / "graph.json").write_text(same)
    (tmp_wiki / ".graph_prev.json").write_text(same)
    result = run_delta_pipeline(tmp_wiki)
    assert result is None


def test_run_delta_pipeline_no_graph_file(tmp_wiki):
    """graph.json이 없으면 None을 반환해야 한다."""
    result = run_delta_pipeline(tmp_wiki)
    assert result is None
