import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import ingest
from ingest import (
    snapshot_graph,
    run_delta_pipeline,
    ingest_file,
    find_unprocessed,
    _get_resonance,
)


@pytest.fixture
def tmp_wiki(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    return wiki_dir


@pytest.fixture
def tmp_raw(tmp_path, monkeypatch):
    """ingest의 RAW_DIR/WIKI_ROOT/STATE_FILE를 tmp_path로 격리한다.

    ingest_file()는 RAW_DIR에 복사하고, find_unprocessed()/_get_resonance()는
    같은 RAW_DIR를 읽으므로 self-contained 검증이 가능하다.
    """
    wiki_root = tmp_path / "brain"
    raw_dir = wiki_root / "raw"
    raw_dir.mkdir(parents=True)
    monkeypatch.setattr(ingest, "WIKI_ROOT", wiki_root)
    monkeypatch.setattr(ingest, "RAW_DIR", raw_dir)
    monkeypatch.setattr(ingest, "STATE_FILE", wiki_root / ".ingest_state.json")
    return wiki_root


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


# ── resonance 보존 (버그 9) ──────────────────────────────────
# WHY: --resonance high로 캡처한 .md/.txt가 --priority-only(=resonance high만)
# 목록에 잡혀야 한다. 기존엔 md/txt는 shutil.copy2만 하고 resonance를
# 비-md/txt의 .extracted.md에만 기록해, 가장 흔한 TIL 포맷(markdown)의
# high 캡처가 조용히 누락됐다.


def test_ingest_md_resonance_high_is_persisted_and_prioritized(tmp_raw):
    """--file x.md --resonance high → resonance가 보존되고 priority-only에 잡힌다."""
    src = tmp_raw / "til.md"
    src.write_text("# TIL\n\n오늘 배운 것.\n")

    dst = ingest_file(src, resonance="high")

    # 복사본에서 resonance 조회가 high여야 한다 (읽는 쪽과 동일 경로).
    assert _get_resonance(dst) == "high"

    # priority-only 목록에 복사본이 포함돼야 한다.
    pending = find_unprocessed(priority_only=True)
    assert dst in pending


def test_ingest_txt_resonance_high_is_persisted_and_prioritized(tmp_raw):
    """.txt도 md와 동일하게 resonance 보존·우선순위 조회가 돼야 한다."""
    src = tmp_raw / "note.txt"
    src.write_text("그냥 평문 메모.\n")

    dst = ingest_file(src, resonance="high")

    assert _get_resonance(dst) == "high"
    pending = find_unprocessed(priority_only=True)
    assert dst in pending


def test_ingest_md_without_resonance_is_unchanged(tmp_raw):
    """resonance 미지정 시 동작 불변 — frontmatter 주입 없이 원본 복사, priority-only 제외."""
    body = "# TIL\n\n출처 없는 평범한 노트.\n"
    src = tmp_raw / "plain.md"
    src.write_text(body)

    dst = ingest_file(src, resonance=None)

    # resonance 미지정이므로 조회 결과 없음.
    assert _get_resonance(dst) is None
    # 원본 내용이 그대로여야 한다 (frontmatter를 임의 주입하지 않음).
    assert dst.read_text() == body
    # priority-only 목록에서 제외돼야 한다.
    pending = find_unprocessed(priority_only=True)
    assert dst not in pending


def test_ingest_md_with_existing_resonance_frontmatter_is_overridden(tmp_raw):
    """원본 frontmatter에 resonance가 있어도 --resonance 인자가 우선 반영돼야 한다."""
    src = tmp_raw / "had-low.md"
    src.write_text("---\ntitle: 기존\nresonance: low\n---\n\n본문\n")

    dst = ingest_file(src, resonance="high")

    assert _get_resonance(dst) == "high"
    pending = find_unprocessed(priority_only=True)
    assert dst in pending
