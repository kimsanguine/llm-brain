"""access_count 갱신 — frontmatter + wiki_stats.json 원자적 동시 갱신.

curate.record_access는 import 시점에 절대경로(curate.WIKI_ROOT)로 바인딩되어
test 격리가 불가능하고 cwd 변경(os.chdir)이라는 전역 side-effect를 요구하므로
재사용하지 않는다. 대신 wiki_root에서 파생한 명시적 경로로 직접 갱신한다.
frontmatter 파싱/직렬화만 curate에서 재사용한다.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path

# scripts/ 를 sys.path에 추가 (기존 컨벤션)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import curate as _curate  # noqa: E402

logger = logging.getLogger(__name__)

# threadpool 동시 호출의 read-modify-write 유실 방지용 프로세스 전역 lock.
_LOCK = threading.Lock()


def track(slug: str, wiki_root: Path | None = None) -> None:
    """페이지 조회 시 access_count를 1 증가시킨다 (best-effort).

    - frontmatter(.md)와 wiki_stats.json을 둘 다 원자적으로 갱신한다.
    - wiki_stats.json 경로는 wiki_root.parent / "wiki_stats.json" (명시적, cwd 무관).
    - 실패는 caller로 raise하지 않고 logger.warning으로 남긴다.

    wiki_root 기본값은 _REPO_ROOT / "wiki" (test에서는 tmp 경로 지정).
    """
    if wiki_root is None:
        wiki_root = _REPO_ROOT / "wiki"
    stats_file = wiki_root.parent / "wiki_stats.json"

    with _LOCK:
        try:
            _update_frontmatter_access(slug, wiki_root)
            _update_stats_access(slug, stats_file)
        except Exception:
            logger.warning("access track 실패 (slug=%s)", slug, exc_info=True)


def _atomic_write_text(path: Path, text: str) -> None:
    """임시 파일에 쓴 뒤 os.replace로 원자적 교체."""
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_name, path)
    except Exception:
        # 교체 실패 시 임시 파일 정리 후 호출자에게 전파 (track이 logging)
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def _update_frontmatter_access(slug: str, wiki_root: Path) -> None:
    """wiki_root 아래에서 slug에 해당하는 .md 파일을 찾아 access_count를 1 증가."""
    matches = list(wiki_root.rglob(f"{slug}.md"))
    if not matches:
        return
    page = matches[0]
    content = page.read_text(encoding="utf-8")
    fm, body = _curate.parse_frontmatter(content)
    fm["access_count"] = int(fm.get("access_count") or 0) + 1
    _atomic_write_text(page, _curate.serialize_frontmatter(fm, body))


def _update_stats_access(slug: str, stats_file: Path) -> None:
    """stats_file(wiki_stats.json)에 slug의 access_count를 1 증가시켜 기록.

    엔트리 형태는 curate.record_access와 동일:
        {"access_count": int, "last_accessed": "YYYY-MM-DD"}
    """
    stats: dict = {}
    if stats_file.exists():
        stats = json.loads(stats_file.read_text(encoding="utf-8"))
    entry = stats.get(slug, {"access_count": 0, "last_accessed": None})
    entry["access_count"] = int(entry.get("access_count") or 0) + 1
    entry["last_accessed"] = datetime.now().strftime("%Y-%m-%d")
    stats[slug] = entry
    _atomic_write_text(
        stats_file,
        json.dumps(stats, ensure_ascii=False, indent=2),
    )
