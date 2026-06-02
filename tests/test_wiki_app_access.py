import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import frontmatter

from wiki_app.access import track


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


def test_track_increments_access_count(tmp_path, monkeypatch):
    # wiki 폴더를 복사한 임시 위치에서 테스트 (실제 wiki를 오염시키지 않기 위해)
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)

    test_page = test_wiki / "business" / "habix-profile.md"
    before = frontmatter.load(test_page).metadata.get("access_count", 0)

    track("habix-profile", wiki_root=test_wiki)

    after = frontmatter.load(test_page).metadata.get("access_count", 0)
    assert after == before + 1


def test_track_unknown_slug_does_not_raise(tmp_path, monkeypatch):
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)
    # 알 수 없는 slug — 조용히 skip (예외 X)
    track("nonexistent-slug-xyz", wiki_root=test_wiki)


# ── self-contained 테스트 (실제 wiki copytree 없이 tmp_path로 직접 생성) ──
# fresh worktree(wiki/ 없음)에서도 실행되도록 wiki를 tmp_path에 직접 만든다.

def _make_wiki(tmp_path: Path, slug: str, access_count: int = 0) -> Path:
    """tmp_path 아래에 최소 wiki 구조를 만들고 wiki_root(=.../wiki)를 반환."""
    wiki_root = tmp_path / "wiki"
    page_dir = wiki_root / "concepts"
    page_dir.mkdir(parents=True)
    page = page_dir / f"{slug}.md"
    page.write_text(
        "---\n"
        f"title: {slug}\n"
        "type: concept\n"
        f"access_count: {access_count}\n"
        "---\n"
        "본문 내용\n"
    )
    return wiki_root


def test_track_increments_frontmatter_and_stats(tmp_path):
    """increment: frontmatter access_count +1 그리고 tmp의 wiki_stats.json 갱신."""
    slug = "alpha"
    wiki_root = _make_wiki(tmp_path, slug, access_count=2)
    page = wiki_root / "concepts" / f"{slug}.md"

    track(slug, wiki_root=wiki_root)

    # frontmatter access_count +1
    assert frontmatter.load(page).metadata["access_count"] == 3

    # stats는 wiki_root.parent (= tmp_path) 아래에 명시적 경로로 기록
    stats_file = wiki_root.parent / "wiki_stats.json"
    assert stats_file.exists()
    stats = json.loads(stats_file.read_text())
    assert stats[slug]["access_count"] == 1
    assert "last_accessed" in stats[slug]


def test_track_no_lost_update_under_concurrency(tmp_path):
    """no-lost-update: N개 스레드가 같은 slug track() 동시 호출 → 최종 == 시작+N."""
    slug = "beta"
    start = 0
    n = 25
    wiki_root = _make_wiki(tmp_path, slug, access_count=start)
    page = wiki_root / "concepts" / f"{slug}.md"

    barrier = threading.Barrier(n)

    def worker():
        barrier.wait()  # 동시 진입 강제
        track(slug, wiki_root=wiki_root)

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert frontmatter.load(page).metadata["access_count"] == start + n

    stats_file = wiki_root.parent / "wiki_stats.json"
    stats = json.loads(stats_file.read_text())
    assert stats[slug]["access_count"] == n


def test_track_does_not_chdir(tmp_path, monkeypatch):
    """no-chdir: os.chdir을 막아도 track()이 정상 동작(=chdir 미사용 증명)."""
    slug = "gamma"
    wiki_root = _make_wiki(tmp_path, slug, access_count=0)
    page = wiki_root / "concepts" / f"{slug}.md"

    import os

    def _forbidden(*args, **kwargs):
        raise AssertionError("track()은 os.chdir을 호출하면 안 된다")

    monkeypatch.setattr(os, "chdir", _forbidden)

    track(slug, wiki_root=wiki_root)

    assert frontmatter.load(page).metadata["access_count"] == 1


def test_track_logs_failure_without_raising(tmp_path, caplog):
    """failure-logged: 실패 유발 시 로그 남고 예외 전파 안 됨.

    wiki_root와 그 parent가 모두 없는 경로 → stats_file 임시파일 생성(mkstemp)이
    존재하지 않는 디렉토리를 가리켜 실패한다. track은 raise하지 않고 logging만 한다.
    """
    import logging

    # ghost/wiki: ghost도 wiki도 존재하지 않음. stats_file.parent(=ghost) 부재.
    bad_root = tmp_path / "ghost" / "wiki"

    with caplog.at_level(logging.WARNING, logger="wiki_app.access"):
        # 예외 전파 없이 리턴해야 한다 (best-effort)
        track("whatever", wiki_root=bad_root)

    assert any(
        record.levelno >= logging.WARNING for record in caplog.records
    ), "실패가 로그로 남아야 한다"
