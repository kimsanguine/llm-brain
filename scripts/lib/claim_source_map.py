"""Deterministic, read-only proposals for explicit single-source claim bindings."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from lib import claim_ledger as ledger
from lib.claim_candidates import classify_candidates
from lib.wiki_frontmatter import load_wiki_post, loads_wiki_post


SCHEMA_VERSION = "llm-brain-claim-source-map/0.1"
_REASONS = frozenset({"no_safe_sources", "no_exact_match", "ambiguous_sources", "non_statement"})


def propose_source_map(slugs: list[str], *, wiki_root: Path) -> dict:
    """Select only a unique declared raw file containing the exact statement."""
    wiki_root = Path(wiki_root)
    project_root = wiki_root.parent
    mappings, unresolved = [], []
    raw_cache = {}
    for slug in sorted(set(slugs)):
        ledger._validate_claim_id(f"claim:{slug}-1")
        page = ledger._find_page_path(slug, wiki_root)
        if page is None:
            raise ledger.ClaimLedgerError("source-map page not found")
        try:
            page_bytes = page.read_bytes()
            post = loads_wiki_post(
                page_bytes.decode("utf-8"),
                allow_legacy_title=page.relative_to(wiki_root).parts[0] == "papers")
        except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
            raise ledger.ClaimLedgerError("cannot read source-map page") from exc
        page_sha = hashlib.sha256(page_bytes).hexdigest()
        sources = {}
        for raw_path in sorted(set(ledger._normalize_sources(post.metadata.get("sources")))):
            if raw_path not in raw_cache:
                try:
                    data = ledger._raw_file(raw_path, project_root).read_bytes()
                    raw_cache[raw_path] = (hashlib.sha256(data).hexdigest(), data.decode("utf-8").splitlines())
                except (OSError, UnicodeError, ledger.ClaimLedgerError):
                    raw_cache[raw_path] = None
            if raw_cache[raw_path] is not None:
                sources[raw_path] = raw_cache[raw_path]
        for candidate in classify_candidates(post.content):
            claim_id = f"claim:{slug}-{candidate['index']}"
            if candidate["exclusion_reason"] is not None:
                unresolved.append({"claim_id": claim_id, "reason": candidate["exclusion_reason"]})
                continue
            statement = candidate["statement"]
            matches = []
            for raw_path, (sha, lines) in sources.items():
                for line_no, line in enumerate(lines, 1):
                    if statement in line:
                        matches.append((raw_path, sha, line_no))
                        break
            if len(matches) != 1:
                reason = "no_safe_sources" if not sources else (
                    "ambiguous_sources" if matches else "no_exact_match")
                unresolved.append({"claim_id": claim_id, "reason": reason})
                continue
            raw_path, sha, line_no = matches[0]
            mappings.append(dict(
                claim_id=claim_id, raw_path=raw_path, raw_sha256=sha,
                locator=f"{raw_path}#L{line_no}-L{line_no}",
                source_binding=dict(
                    schema_version="llm-brain-claim-binding/0.1",
                    page_sha256=page_sha,
                    statement_sha256=hashlib.sha256(statement.encode("utf-8")).hexdigest(),
                    quote=statement,
                ),
            ))
    return dict(schema_version=SCHEMA_VERSION, mappings=mappings, unresolved=unresolved)


def read_source_map(path: Path) -> dict[str, dict]:
    """Load the complete manifest strictly before a caller can write any ledger."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=ledger._unique_json_fields)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ledger.ClaimLedgerError("cannot read source map") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "mappings", "unresolved"}:
        raise ledger.ClaimLedgerError("invalid source-map fields")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ledger.ClaimLedgerError("unsupported source-map version")
    if not isinstance(data["mappings"], list) or not isinstance(data["unresolved"], list):
        raise ledger.ClaimLedgerError("source-map entries must be lists")
    result, seen = {}, set()
    for raw in data["mappings"]:
        value = ledger.validate_source_selection(raw)
        claim_id = value["claim_id"]
        if claim_id in seen:
            raise ledger.ClaimLedgerError("duplicate source-map claim")
        seen.add(claim_id)
        result[claim_id] = value
    for raw in data["unresolved"]:
        if not isinstance(raw, dict) or set(raw) != {"claim_id", "reason"}:
            raise ledger.ClaimLedgerError("invalid unresolved source-map fields")
        claim_id = ledger._validate_claim_id(raw["claim_id"])
        if not isinstance(raw["reason"], str) or raw["reason"] not in _REASONS:
            raise ledger.ClaimLedgerError("invalid unresolved source-map reason")
        if claim_id in seen:
            raise ledger.ClaimLedgerError("duplicate source-map claim")
        seen.add(claim_id)
    return result


def unmapped_count(slugs: list[str], *, wiki_root: Path, mapped_count: int) -> int:
    wiki_root = Path(wiki_root)
    count = 0
    for slug in set(slugs):
        path = ledger._find_page_path(slug, wiki_root)
        if path is not None:
            post = load_wiki_post(
                path, allow_legacy_title=path.relative_to(wiki_root).parts[0] == "papers")
            count += len(ledger._split_claims(post.content))
    return count - mapped_count
