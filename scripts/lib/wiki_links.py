"""Shared, deterministic wikilink parsing and page resolution."""
from __future__ import annotations

import re
from collections.abc import Collection


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]+)?\]\]")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def extract_wikilinks(text: str) -> set[str]:
    return set(WIKILINK_RE.findall(_FRONTMATTER_RE.sub("", text, count=1)))


def resolve_wikilink(target: str, pages: Collection[str]) -> str | None:
    """Exact slug wins; a basename resolves only to one nested page."""
    if target in pages:
        return target
    matches = [page for page in pages if page.endswith('/' + target)]
    return matches[0] if len(matches) == 1 else None
