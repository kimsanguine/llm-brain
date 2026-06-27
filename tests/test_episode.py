"""episode.py — append-only 에피소드 원장 계약 테스트 (Phase 0, PRD US-001).

WHY (이 테스트가 인코딩하는 의도):
  1. 헬퍼는 fail-loud — 필수 키 누락·타입오류·잘못된 timestamp 는 EpisodeSchemaError
     (조용히 깨진 레코드를 원장에 쌓지 않는다). 단, *호출측* 의 fail-soft 는 Phase 1.
  2. append-only — 기존 줄은 절대 재작성하지 않는다(운영 이력의 무결성).
  3. 월별 샤드 — timestamp 의 YYYY-MM 으로 episodes/YYYY-MM.jsonl 에 적재.
  4. read_recent — 최신순(timestamp desc) 결정적 정렬 + task_type/topic 필터.

episodes_dir 를 tmp_path 로 주입해 사용자 episodes/ 를 건드리지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import episode  # noqa: E402


def _rec(**over):
    base = dict(
        timestamp="2026-06-27T07:30:00+09:00",
        task_type="ai_answer",
        user_goal="RAG 질문",
        inputs={},
        read_pages=[],
        procedures_used=[],
        outputs={},
        status="ok",
        notes="",
    )
    base.update(over)
    return base


# ── append: 정상 ───────────────────────────────────────────────
def test_append_writes_jsonl_line_to_month_shard(tmp_path):
    episode.append(_rec(), episodes_dir=tmp_path)
    shard = tmp_path / "2026-06.jsonl"
    assert shard.exists()
    lines = shard.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["task_type"] == "ai_answer"


def test_append_is_append_only(tmp_path):
    episode.append(_rec(notes="first"), episodes_dir=tmp_path)
    episode.append(_rec(notes="second"), episodes_dir=tmp_path)
    lines = (tmp_path / "2026-06.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["notes"] == "first"  # 첫 줄 보존


def test_append_unicode_preserved(tmp_path):
    episode.append(_rec(user_goal="한국어 목표"), episodes_dir=tmp_path)
    raw = (tmp_path / "2026-06.jsonl").read_text(encoding="utf-8")
    assert "한국어 목표" in raw  # ensure_ascii=False


def test_append_derives_shard_from_timestamp_month(tmp_path):
    episode.append(_rec(timestamp="2026-07-02T10:00:00+09:00"), episodes_dir=tmp_path)
    assert (tmp_path / "2026-07.jsonl").exists()
    assert not (tmp_path / "2026-06.jsonl").exists()


# ── append: fail-loud ──────────────────────────────────────────
def test_append_missing_required_key_raises_and_writes_nothing(tmp_path):
    bad = _rec()
    del bad["status"]
    with pytest.raises(episode.EpisodeSchemaError):
        episode.append(bad, episodes_dir=tmp_path)
    assert list(tmp_path.glob("*.jsonl")) == []  # 부분 기록 0


def test_append_wrong_type_raises(tmp_path):
    with pytest.raises(episode.EpisodeSchemaError):
        episode.append(_rec(read_pages="wiki/x.md"), episodes_dir=tmp_path)  # str, list 여야


def test_append_bad_timestamp_raises(tmp_path):
    with pytest.raises(episode.EpisodeSchemaError):
        episode.append(_rec(timestamp="not-a-date"), episodes_dir=tmp_path)


# ── read_recent ────────────────────────────────────────────────
def test_read_recent_returns_timestamp_desc(tmp_path):
    episode.append(_rec(timestamp="2026-06-01T00:00:00+09:00", notes="old"), episodes_dir=tmp_path)
    episode.append(_rec(timestamp="2026-06-27T00:00:00+09:00", notes="new"), episodes_dir=tmp_path)
    got = episode.read_recent(episodes_dir=tmp_path)
    assert [r["notes"] for r in got] == ["new", "old"]  # 최신순


def test_read_recent_filters_by_task_type(tmp_path):
    episode.append(_rec(task_type="ai_answer"), episodes_dir=tmp_path)
    episode.append(_rec(task_type="express_blog"), episodes_dir=tmp_path)
    got = episode.read_recent(task_type="express_blog", episodes_dir=tmp_path)
    assert len(got) == 1 and got[0]["task_type"] == "express_blog"


def test_read_recent_filters_by_topic_keyword(tmp_path):
    episode.append(_rec(user_goal="RAG 평가 파이프라인"), episodes_dir=tmp_path)
    episode.append(_rec(user_goal="영상 자막 번역"), episodes_dir=tmp_path)
    got = episode.read_recent(topic="RAG", episodes_dir=tmp_path)
    assert len(got) == 1 and "RAG" in got[0]["user_goal"]


def test_read_recent_respects_limit(tmp_path):
    for i in range(5):
        episode.append(_rec(timestamp=f"2026-06-0{i+1}T00:00:00+09:00"), episodes_dir=tmp_path)
    assert len(episode.read_recent(limit=2, episodes_dir=tmp_path)) == 2


def test_read_recent_empty_when_no_episodes(tmp_path):
    assert episode.read_recent(episodes_dir=tmp_path) == []
