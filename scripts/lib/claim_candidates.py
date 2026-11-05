"""Conservative structural classification after the stable legacy claim split."""
from __future__ import annotations

from bisect import bisect_right
import re

from lib import claim_ledger as ledger


_HEADING_RE = re.compile(r"^#{1,6}(?:\s|$)")
_SEPARATOR_RE = re.compile(r"(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,}|={3,}")
_SETEXT_RE = re.compile(r"(?:={3,}|-{3,})\s*")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_BULLET_RE = re.compile(r"^(?:[-+*]|\d+[.)])\s+")
_LINK_TOKEN = (
    r"!?\[[^\]\n]*\]\((?:[^()\n]|\([^()\n]*\))*\)"
    r"|!?\[\[[^\]\n]+\]\]|<https?://[^<>\s]+>|https?://[^\s<>]+"
)
_LINK_ONLY_RE = re.compile(rf"(?:{_LINK_TOKEN})(?:\s+(?:{_LINK_TOKEN}))*[.!?]?")
_METADATA_RE = re.compile(
    r"(?:\*\*)?(?:title|tags|sources?|url|author|created|updated|published|doi|arxiv)"
    r"(?:\*\*)?\s*:.*", re.IGNORECASE)
_LINK_DEFINITION_RE = re.compile(r"\[[^\]\n]+\]:\s*\S+.*")


def _fragment_kind(text: str) -> str:
    text = text.strip()
    if _HEADING_RE.match(text):
        return "heading"
    if _SEPARATOR_RE.fullmatch(text):
        return "separator"
    fragment = _BULLET_RE.sub("", text, count=1)
    if (_METADATA_RE.fullmatch(fragment) or _LINK_DEFINITION_RE.fullmatch(fragment)
            or (fragment.startswith("<!--") and fragment.endswith("-->"))):
        return "metadata"
    if _LINK_ONLY_RE.fullmatch(fragment):
        return "image" if fragment.startswith("!") else "link"
    return "text"


def _line_kinds(lines: list[str]) -> list[str]:
    kinds = []
    fence_char, fence_size = None, 0
    for line in lines:
        fence = _FENCE_RE.match(line)
        if fence_char is not None:
            kinds.append("code")
            if (fence and fence[1][0] == fence_char and len(fence[1]) >= fence_size
                    and not fence[2].strip()):
                fence_char, fence_size = None, 0
        elif fence and (fence[1][0] != "`" or "`" not in fence[2]):
            kinds.append("code")
            fence_char, fence_size = fence[1][0], len(fence[1])
        else:
            kinds.append(_fragment_kind(line))

    for index, line in enumerate(lines):
        if kinds[index] == "code":
            continue
        stripped = line.strip()
        if index and _SETEXT_RE.fullmatch(stripped) and lines[index - 1].strip():
            if kinds[index - 1] == "text" and not _BULLET_RE.match(lines[index - 1].strip()):
                kinds[index - 1] = "heading"
        cells = stripped.strip("|").split("|")
        if len(cells) < 2 or not all(re.fullmatch(r"\s*:?-{3,}:?\s*", cell) for cell in cells):
            continue
        kinds[index] = "table"
        if index and "|" in lines[index - 1] and kinds[index - 1] == "text":
            kinds[index - 1] = "table"
        following = index + 1
        while following < len(lines) and "|" in lines[following] and kinds[following] != "code":
            kinds[following] = "table"
            following += 1
    return kinds


def classify_candidates(body: str) -> list[dict]:
    """Return unchanged split text/indexes; structure is not semantic validation.

    Original line context identifies split heading fragments and every line in
    a fenced block, including code with no Markdown markers of its own.
    """
    lines = body.split("\n")
    kinds = _line_kinds(lines)
    starts, offset = [], 0
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1
    result, cursor = [], 0
    for index, statement in enumerate(ledger._split_claims(body), 1):
        position = body.index(statement, cursor)
        cursor = position + len(statement)
        line_kind = kinds[bisect_right(starts, position) - 1]
        kind = _fragment_kind(statement) if line_kind == "text" else line_kind
        result.append(dict(index=index, statement=statement, kind=kind,
                           exclusion_reason=None if kind == "text" else "non_statement"))
    return result
