"""claim_ledger — file-first claim provenance + safe query context helpers.

query 응답에서 wiki 본문 전체를 무차별 투입하지 않고, current claim만 raw provenance와
함께 LLM 에 건네기 위한 작은 결정적 원장이다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import hashlib
import re
from pathlib import Path
from typing import Iterable

import frontmatter


_CATEGORIES = ("concepts", "tools", "people", "projects", "business", "lecture", "insights")
_CLAIM_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_CITATION_RE = re.compile(r"\[claim:([A-Za-z0-9_/\-]+)\]")
_OPINION_MARKERS = ("권장", "추천", "의견", "생각", "should", "prefer")
_INFERENCE_MARKERS = ("아마", "추정", "가능성", "보인다", "might", "may", "could")
_UNTRUSTED_DIR_MARKERS = ("/newsletters/", "/clippings/", "/captures/")
_VALIDITY_WINDOW_DAYS = 180


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    slug: str
    text: str
    classification: str
    source_path: str
    source_locator: str
    source_sha256: str
    status: str
    valid_from: str
    valid_until: str


def _find_page_path(slug: str, wiki_root: Path) -> Path | None:
    for cat in _CATEGORIES:
        candidate = wiki_root / cat / f"{slug}.md"
        if candidate.exists():
            return candidate
    return None


def _normalize_sources(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if value:
        return [str(value)]
    return []


def _split_claims(body: str) -> list[str]:
    claims: list[str] = []
    for part in _CLAIM_SPLIT_RE.split(body.strip()):
        claim = part.strip()
        if claim:
            claims.append(claim)
    return claims


def _classification(text: str) -> str:
    low = text.lower()
    if any(marker.lower() in low for marker in _OPINION_MARKERS):
        return "opinion"
    if any(marker.lower() in low for marker in _INFERENCE_MARKERS):
        return "inference"
    return "fact"


def _parse_date(raw, *, fallback: date) -> date:
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str) and raw:
        return date.fromisoformat(raw[:10])
    return fallback


def _is_untrusted_source(source_path: str) -> bool:
    if source_path.startswith(("http://", "https://")):
        return True
    norm = "/" + source_path.strip("/")
    return any(marker in norm for marker in _UNTRUSTED_DIR_MARKERS)


def _source_file(source_path: str, wiki_root: Path) -> Path | None:
    if source_path.startswith(("http://", "https://")):
        return None
    candidate = wiki_root.parent / source_path
    return candidate if candidate.exists() else None


def _source_sha256(source_path: str, claim_text: str, wiki_root: Path) -> str:
    source_file = _source_file(source_path, wiki_root)
    if source_file is not None:
        return hashlib.sha256(source_file.read_bytes()).hexdigest()
    return hashlib.sha256(claim_text.encode("utf-8")).hexdigest()


def _source_locator(source_path: str, claim_text: str, wiki_root: Path) -> str:
    source_file = _source_file(source_path, wiki_root)
    if source_file is None:
        return source_path

    needle = claim_text.strip()
    for idx, line in enumerate(source_file.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if needle and needle in line:
            return f"{source_path}#L{idx}-L{idx}"
    return source_path


def _is_superseded(text: str, superseded_claims: Iterable[str]) -> bool:
    stripped = text.strip()
    for item in superseded_claims:
        candidate = str(item).strip()
        if candidate and (candidate in stripped or stripped in candidate):
            return True
    return False


def _status(
    *,
    claim_text: str,
    superseded_claims: list[str],
    gate_status: str,
    source_path: str,
    valid_until: date,
    today: date,
) -> str:
    if _is_superseded(claim_text, superseded_claims) or gate_status == "rejected":
        return "superseded"
    if valid_until < today:
        return "stale"
    if _is_untrusted_source(source_path):
        return "untrusted"
    return "active"


def build_claim_ledger(slugs: list[str], *, wiki_root: Path, now: date | datetime | None = None) -> list[ClaimRecord]:
    today = now.date() if isinstance(now, datetime) else (now or date.today())
    ledger: list[ClaimRecord] = []

    for slug in slugs:
        page_path = _find_page_path(slug, wiki_root)
        if page_path is None:
            continue
        post = frontmatter.load(page_path)
        fm = post.metadata
        body = post.content
        claims = _split_claims(body)
        sources = _normalize_sources(fm.get("sources"))
        source_path = sources[0] if sources else str(page_path.relative_to(wiki_root.parent))
        valid_from_d = _parse_date(fm.get("updated") or fm.get("created"), fallback=today)
        valid_until_d = _parse_date(
            fm.get("observation_expires"),
            fallback=valid_from_d + timedelta(days=_VALIDITY_WINDOW_DAYS),
        )
        superseded_claims = [str(v) for v in (fm.get("superseded_claims") or [])]
        gate_status = str(fm.get("gate_status") or "")

        for idx, claim_text in enumerate(claims, start=1):
            ledger.append(
                ClaimRecord(
                    claim_id=f"claim:{slug}-{idx}",
                    slug=slug,
                    text=claim_text,
                    classification=_classification(claim_text),
                    source_path=source_path,
                    source_locator=_source_locator(source_path, claim_text, wiki_root),
                    source_sha256=_source_sha256(source_path, claim_text, wiki_root),
                    status=_status(
                        claim_text=claim_text,
                        superseded_claims=superseded_claims,
                        gate_status=gate_status,
                        source_path=source_path,
                        valid_until=valid_until_d,
                        today=today,
                    ),
                    valid_from=valid_from_d.isoformat(),
                    valid_until=valid_until_d.isoformat(),
                )
            )
    return ledger


def render_llm_context(ledger: list[ClaimRecord]) -> str:
    trusted = [c for c in ledger if c.status == "active"]
    untrusted = [c for c in ledger if c.status == "untrusted"]

    lines = ["## trusted claim ledger", ""]
    if trusted:
        for claim in trusted:
            lines.append(
                f"- [{claim.claim_id}] {claim.classification} | {claim.source_locator} "
                f"| sha256:{claim.source_sha256[:12]} | valid {claim.valid_from}..{claim.valid_until}"
            )
            lines.append(f"  {claim.text}")
    else:
        lines.append("(trusted current claim 없음)")

    lines.extend(["", "## 외부 캡처 원문 (검증 전)", ""])
    if untrusted:
        for claim in untrusted:
            lines.append(
                f"- [{claim.claim_id}] untrusted | {claim.source_locator} "
                f"| sha256:{claim.source_sha256[:12]} | valid {claim.valid_from}..{claim.valid_until}"
            )
            lines.append(f"  {claim.text}")
    else:
        lines.append("(검증 전 외부 캡처 없음)")
    return "\n".join(lines)


def render_cited_answer(answer: str, ledger: list[ClaimRecord]) -> str:
    current = {c.claim_id: c for c in ledger if c.status in {"active", "untrusted"}}
    used_ids: list[str] = []

    def replace(match: re.Match[str]) -> str:
        claim_id = f"claim:{match.group(1)}"
        if claim_id not in current:
            return ""
        if claim_id not in used_ids:
            used_ids.append(claim_id)
        return match.group(0)

    cleaned = _CITATION_RE.sub(replace, answer).strip()
    if not used_ids:
        return cleaned

    lines = [cleaned, "", "## 출처"]
    for claim_id in used_ids:
        claim = current[claim_id]
        lines.append(
            f"- [{claim.claim_id}] {claim.classification} · {claim.source_locator} "
            f"· sha256:{claim.source_sha256[:12]} · valid {claim.valid_from}..{claim.valid_until}"
        )
    return "\n".join(lines)
