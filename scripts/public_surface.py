#!/usr/bin/env python3
"""Reject directories that are intentionally local/private in public source."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


FORBIDDEN = frozenset({"docs", ".archive"})
EXCLUDED = frozenset({".git", ".worktrees", "worktrees", ".venv", "__pycache__"})


def violations(root: Path) -> set[str]:
    root = Path(root)
    found: set[str] = set()
    if (root / '.git').exists():
        indexed = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--stage', '-z'])
        for entry in indexed.decode('utf-8').split('\0'):
            if not entry:
                continue
            metadata, filename = entry.split('\t', 1)
            mode = metadata.split(' ', 1)[0]
            parts = Path(filename).parts
            if mode not in {'120000', '160000'}:
                parts = parts[:-1]
            for depth in range(1, len(parts) + 1):
                if FORBIDDEN.intersection(parts[:depth]):
                    found.add(Path(*parts[:depth]).as_posix())
        return found
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
