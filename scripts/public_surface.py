#!/usr/bin/env python3
"""Reject directories that are intentionally local/private in public source."""

from __future__ import annotations

import argparse
from pathlib import Path


FORBIDDEN = frozenset({"docs", ".archive"})
EXCLUDED = frozenset({".git", ".worktrees", "worktrees", ".venv", "__pycache__"})


def violations(root: Path) -> set[str]:
    root = Path(root)
    found: set[str] = set()
    for candidate in root.rglob("*"):
        if not candidate.is_dir():
            continue
        relative = candidate.relative_to(root)
        if EXCLUDED.intersection(relative.parts):
            continue
        if FORBIDDEN.intersection(relative.parts):
            found.add(relative.as_posix())
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="validate public repository paths")
    parser.add_argument("root", nargs="?", default=Path(__file__).parents[1], type=Path)
    args = parser.parse_args()
    found = sorted(violations(args.root))
    if found:
        raise SystemExit("forbidden public path(s): " + ", ".join(found))
    print("public surface: valid")


if __name__ == "__main__":
    main()
