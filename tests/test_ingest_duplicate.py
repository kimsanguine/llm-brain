"""is_duplicate() characterization 테스트 — v0.3.0 재배선 전 현 동작 고정.

이 테스트들은 "현재가 옳다"를 단언하는 것이 아니라 "현재가 이렇다"를 기록한다.
is_duplicate()는 곧 저장 전 호출 + hard-block으로 재배선될 예정이므로,
수정 전 회귀 기준선으로 아래 관측된 동작을 그대로 고정한다:

- index.md의 [[wikilink]] 목록과 파일명 slug를 대조해 bool 반환.
- slug 정규화: 날짜 접두사(YYYY-MM-DD-) 제거, `_`→`-`, 소문자화.
- 중복이면 경고 print + True 반환하되 예외를 던지지 않는다 (soft 계약).
- index.md 부재 시 False (조기 반환).
- 호출부(ingest.py main)는 반환값을 버린다 — 저장이 끝난 뒤 호출됨.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import ingest
from ingest import is_duplicate


@pytest.fixture
def tmp_brain(tmp_path, monkeypatch):
    """ingest의 WIKI_ROOT를 tmp_path로 격리한다 (test_ingest_delta.py 패턴)."""
    wiki_root = tmp_path / "brain"
    raw_dir = wiki_root / "raw"
    raw_dir.mkdir(parents=True)
    monkeypatch.setattr(ingest, "WIKI_ROOT", wiki_root)
    monkeypatch.setattr(ingest, "RAW_DIR", raw_dir)
    monkeypatch.setattr(ingest, "STATE_FILE", wiki_root / ".ingest_state.json")
    return wiki_root


def _write_index(wiki_root: Path, body: str) -> None:
    (wiki_root / "index.md").write_text(body)


# ---------------------------------------------------------------------------
# ① 동일 slug 중복 감지 → True
# ---------------------------------------------------------------------------

def test_duplicate_slug_returns_true(tmp_brain):
    """index.md에 같은 slug의 [[wikilink]]가 있으면 True."""
    _write_index(tmp_brain, "# Index\n\n- [[agent-memory]]\n")
    file = tmp_brain / "raw" / "agent-memory.md"
    assert is_duplicate(file) is True


def test_duplicate_with_alias_wikilink_returns_true(tmp_brain):
    """[[slug|표시명]] alias 형태 wikilink도 slug 부분으로 매칭한다."""
    _write_index(tmp_brain, "- [[agent-memory|에이전트 메모리]]\n")
    file = tmp_brain / "raw" / "agent-memory.md"
    assert is_duplicate(file) is True


# ---------------------------------------------------------------------------
# ② 비중복 → False
# ---------------------------------------------------------------------------

def test_non_duplicate_returns_false(tmp_brain):
    _write_index(tmp_brain, "- [[agent-memory]]\n- [[rag-pipeline]]\n")
    file = tmp_brain / "raw" / "totally-new-topic.md"
    assert is_duplicate(file) is False


# ---------------------------------------------------------------------------
# ③ slug 정규화: 날짜 접두사 제거 · 언더스코어→하이픈 · 소문자
# ---------------------------------------------------------------------------

def test_date_prefix_is_stripped_before_compare(tmp_brain):
    """파일명의 YYYY-MM-DD- 접두사는 slug 비교 전에 제거된다."""
    _write_index(tmp_brain, "- [[agent-memory]]\n")
    file = tmp_brain / "raw" / "2026-07-04-agent-memory.md"
    assert is_duplicate(file) is True


def test_underscore_normalized_to_hyphen(tmp_brain):
    """파일명 언더스코어는 하이픈으로 정규화된다."""
    _write_index(tmp_brain, "- [[agent-memory]]\n")
    file = tmp_brain / "raw" / "agent_memory.md"
    assert is_duplicate(file) is True


def test_case_insensitive_on_both_sides(tmp_brain):
    """파일명 stem과 index wikilink 모두 소문자화 후 비교한다."""
    _write_index(tmp_brain, "- [[Agent-Memory]]\n")
    file = tmp_brain / "raw" / "AGENT-MEMORY.md"
    assert is_duplicate(file) is True


def test_all_normalizations_combined(tmp_brain):
    """날짜 접두사 + 언더스코어 + 대문자가 겹쳐도 정규화 후 매칭한다."""
    _write_index(tmp_brain, "- [[agent-memory]]\n")
    file = tmp_brain / "raw" / "2026-01-01-Agent_Memory.md"
    assert is_duplicate(file) is True


def test_path_containing_wikilink_is_not_matched(tmp_brain):
    """(현 동작 기록) `/`가 든 wikilink([[concepts/agent-memory]])는
    regex `[^\\]|/]`에서 제외돼 slug로 추출되지 않는다 → 중복 미감지(False).
    """
    _write_index(tmp_brain, "- [[concepts/agent-memory]]\n")
    file = tmp_brain / "raw" / "agent-memory.md"
    assert is_duplicate(file) is False


# ---------------------------------------------------------------------------
# ④ index.md 부재 / 빈 파일
# ---------------------------------------------------------------------------

def test_missing_index_returns_false(tmp_brain):
    """index.md가 없으면 조기 False (예외 없음)."""
    file = tmp_brain / "raw" / "agent-memory.md"
    assert is_duplicate(file) is False


def test_empty_index_returns_false(tmp_brain):
    """index.md가 빈 파일이면 wikilink 0개 → False."""
    _write_index(tmp_brain, "")
    file = tmp_brain / "raw" / "agent-memory.md"
    assert is_duplicate(file) is False


# ---------------------------------------------------------------------------
# ⑤ soft 계약: 중복이어도 예외를 던지지 않고 경고만 출력
# ---------------------------------------------------------------------------

def test_duplicate_is_soft_prints_warning_no_exception(tmp_brain, capsys):
    """중복 감지 시 예외 없이 True 반환 + '[경고]' 메시지 출력 (soft 계약).

    호출부(main)는 이 반환값을 버리므로 ingest는 중단되지 않는다 —
    v0.3.0에서 hard-block으로 바뀌면 이 계약이 깨지는 것이 의도된 변경이다.
    """
    _write_index(tmp_brain, "- [[agent-memory]]\n")
    file = tmp_brain / "raw" / "agent-memory.md"

    result = is_duplicate(file)  # 예외가 나면 테스트 실패

    assert result is True
    out = capsys.readouterr().out
    assert "[경고]" in out
    assert "agent-memory" in out


def test_non_duplicate_prints_nothing(tmp_brain, capsys):
    """비중복이면 출력 없이 False만 반환한다."""
    _write_index(tmp_brain, "- [[other-topic]]\n")
    file = tmp_brain / "raw" / "agent-memory.md"

    assert is_duplicate(file) is False
    assert capsys.readouterr().out == ""


def test_file_itself_need_not_exist(tmp_brain):
    """(현 동작 기록) is_duplicate는 파일명(stem)만 보므로
    대상 파일이 디스크에 없어도 예외 없이 동작한다."""
    _write_index(tmp_brain, "- [[agent-memory]]\n")
    ghost = tmp_brain / "raw" / "agent-memory.md"  # 미생성
    assert not ghost.exists()
    assert is_duplicate(ghost) is True
