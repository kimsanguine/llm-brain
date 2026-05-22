"""access_count 갱신 wrapper — scripts/curate.record_access 재사용."""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/ 를 sys.path에 추가 (기존 컨벤션)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import curate as _curate  # noqa: E402


def track(slug: str, wiki_root: Path | None = None) -> None:
    """페이지 조회 시 access_count를 1 증가시킨다.

    wiki_root 인자는 test 격리용. 기본은 curate.record_access의 cwd 기반 동작.
    """
    if wiki_root is not None:
        # curate.record_access는 cwd 기반이라 호출 직전에 cwd 변경
        import os
        original = os.getcwd()
        os.chdir(wiki_root.parent)
        try:
            _curate.record_access(slug)
        except Exception:
            # 알 수 없는 slug 등 — 조용히 skip
            pass
        finally:
            os.chdir(original)
        # wiki 파일 frontmatter의 access_count도 갱신
        _update_frontmatter_access(slug, wiki_root)
    else:
        try:
            _curate.record_access(slug)
        except Exception:
            pass
        # 기본 cwd 기반 wiki dir 사용
        _update_frontmatter_access(slug, _REPO_ROOT / "wiki")


def _update_frontmatter_access(slug: str, wiki_root: Path) -> None:
    """wiki_root 아래에서 slug에 해당하는 .md 파일을 찾아 access_count를 1 증가."""
    matches = list(wiki_root.rglob(f"{slug}.md"))
    if not matches:
        return
    page = matches[0]
    try:
        content = page.read_text()
        fm, body = _curate.parse_frontmatter(content)
        fm["access_count"] = int(fm.get("access_count") or 0) + 1
        page.write_text(_curate.serialize_frontmatter(fm, body))
    except Exception:
        pass
