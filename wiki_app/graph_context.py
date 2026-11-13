"""Read-only, bounded graph context assembled from current wiki and claims."""
from __future__ import annotations

import json
from pathlib import Path
import re
import yaml

from lib import claim_ledger
from lib.ontology_projection import safe_slug
from lib.wiki_frontmatter import load_wiki_post
from lib.wiki_links import WIKILINK_RE, extract_wikilinks, resolve_wikilink


MAX_CLAIMS_PER_PAGE = 20
MAX_ANCHORS_PER_EDGE = 3
MAX_EXCERPT_CHARS = 400
MAX_STATEMENT_CHARS = 1000


class PreviewError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _paragraphs(body: str):
    text = body.strip()
    spans, start = [], 0
    for separator in re.finditer(r'\n[ \t]*\n', text):
        spans.append((start, separator.start()))
        start = separator.end()
    spans.append((start, len(text)))
    return text, spans


def _anchors(body: str, target: str, page_ids: set[str]):
    text, spans = _paragraphs(body)
    result = []
    for index, (start, end) in enumerate(spans):
        paragraph = text[start:end]
        if any(resolve_wikilink(link, page_ids) == target for link in WIKILINK_RE.findall(paragraph)):
            result.append((index, paragraph))
    return result


def _claim_paragraph(body: str, claim):
    text, blocks = _paragraphs(body)
    start = 0
    statements = []
    for separator in claim_ledger._CLAIM_SPLIT_RE.finditer(text):
        part = text[start:separator.start()]
        if part.strip():
            statements.append((part.strip(), start + len(part) - len(part.lstrip())))
        start = separator.end()
    part = text[start:]
    if part.strip():
        statements.append((part.strip(), start + len(part) - len(part.lstrip())))
    position = int(claim.claim_id.rsplit('-', 1)[1]) - 1
    if position >= len(statements) or statements[position][0] != claim.statement:
        return None
    offset = statements[position][1]
    return next((i for i, (start, end) in enumerate(blocks) if start <= offset < end), None)


def _anchor_summary(anchors):
    locations = []
    for index, paragraph in anchors[:MAX_ANCHORS_PER_EDGE]:
        locations.append({'paragraph':index + 1, 'excerpt':paragraph[:MAX_EXCERPT_CHARS],
                          'truncated':len(paragraph) > MAX_EXCERPT_CHARS})
    return {'total':len(anchors), 'locations':locations,
            'omitted':max(0, len(anchors) - len(locations))}


def _read_pages(wiki: Path):
    posts = {}
    for category in claim_ledger._CATEGORIES:
        for path in sorted((wiki/category).rglob('*.md')):
            if not path.resolve().is_relative_to(wiki):
                raise PreviewError('wiki_invalid')
            slug = safe_slug(path.relative_to(wiki/category).with_suffix('').as_posix())
            if slug in posts:
                raise PreviewError('wiki_invalid')
            posts[slug] = load_wiki_post(path, allow_legacy_title=category == 'papers')
            if posts[slug].metadata.get('scope', 'shared') not in {'private', 'shared'}:
                raise PreviewError('wiki_invalid')
    return posts


def _checked_graph(wiki: Path, posts):
    path = wiki/'graph.json'
    if not path.exists():
        raise PreviewError('graph_missing')
    try:
        if not path.resolve().is_relative_to(wiki.resolve()):
            raise ValueError
        graph = json.loads(path.read_text(encoding='utf-8'))
        nodes, links = graph['nodes'], graph['links']
        if not isinstance(nodes, list) or not isinstance(links, list):
            raise ValueError
        page_ids = [n['id'] for n in nodes if n['kind'] == 'page']
        if len(page_ids) != len(set(page_ids)):
            raise ValueError
        page_set = set(page_ids)
        if page_set != set(posts):
            raise PreviewError('graph_stale')
        stored = []
        for edge in links:
            if edge['kind'] == 'wikilink':
                source, target = edge['source'], edge['target']
                if source not in page_set or target not in page_set or source == target:
                    raise ValueError
                stored.append((source, target))
        if len(stored) != len(set(stored)):
            raise ValueError
    except PreviewError:
        raise
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        raise PreviewError('graph_invalid') from None
    actual = set()
    for slug, post in posts.items():
        for target in extract_wikilinks(post.content):
            resolved = resolve_wikilink(target, page_set)
            if resolved is not None and resolved != slug:
                actual.add((slug, resolved))
    if actual != set(stored):
        raise PreviewError('graph_stale')
    meta = graph.get('meta', {})
    if not isinstance(meta, dict):
        raise PreviewError('graph_invalid')
    return actual, meta.get('generated')


def _claim_info(claim, root: Path, body: str, anchor_indices: set[int] | None):
    try:
        claim_ledger.validate_claim_source_inventory([claim], wiki_root=root/'wiki')
    except claim_ledger.ClaimSourceInventoryError:
        return {'id':claim.claim_id, 'eligibility':'inventory_invalid', 'link_context':'unknown'}
    reason = claim_ledger.claim_exclusion_reason(claim, project_root=root) or 'usable'
    position = _claim_paragraph(body, claim)
    if anchor_indices is None:
        context = 'unknown'
    elif position is None:
        context = 'position_unverified'
    elif position in anchor_indices:
        context = 'same_paragraph'
    elif any(abs(position - index) == 1 for index in anchor_indices):
        context = 'adjacent_paragraph'
    else:
        context = 'other_paragraph'
    return {'id':claim.claim_id, 'statement':claim.statement[:MAX_STATEMENT_CHARS],
            'statement_truncated':len(claim.statement) > MAX_STATEMENT_CHARS,
            'eligibility':reason, 'status':claim.status, 'trust':claim.trust,
            'valid_until':claim.valid_until, 'link_context':context,
            'source':{'raw_path':claim.raw_path, 'locator':claim.locator}}


def _claim_list(records, root: Path, body: str, anchor_indices):
    records = sorted(records, key=lambda record:record.claim_id)
    selected = records[:MAX_CLAIMS_PER_PAGE]
    return {'claims':[_claim_info(c, root, body, anchor_indices) for c in selected],
            'claims_total':len(records), 'claims_omitted':len(records)-len(selected)}


def build_preview(wiki: Path, *, seed: str, question: str, offset: int, limit: int):
    wiki = wiki.resolve()
    root = wiki.parent
    try:
        posts = _read_pages(wiki)
        if seed not in posts:
            raise PreviewError('seed_not_found')
        edges, generated = _checked_graph(wiki, posts)
        ledger = root/'claims.jsonl'
        if not ledger.exists():
            raise PreviewError('ledger_missing')
        if not ledger.resolve().is_relative_to(root):
            raise PreviewError('ledger_invalid')
        try:
            records = claim_ledger.read_claims_jsonl(ledger)
        except claim_ledger.ClaimLedgerError:
            raise PreviewError('ledger_invalid') from None
        if posts and not records:
            raise PreviewError('ledger_invalid')
        grouped = {}
        for record in records:
            grouped.setdefault(claim_ledger.claim_slug(record), []).append(record)
        try:
            claim_ledger.validate_claim_source_inventory(grouped.get(seed, []), wiki_root=wiki)
        except claim_ledger.ClaimSourceInventoryError:
            raise PreviewError('seed_inventory_invalid') from None
        incoming = {a for a,b in edges if b == seed}
        outgoing = {b for a,b in edges if a == seed}
        ordered = sorted(incoming | outgoing)
        neighbors = []
        for slug in ordered[offset:offset+limit]:
            in_anchors = _anchors(posts[slug].content, seed, set(posts)) if slug in incoming else []
            out_anchors = _anchors(posts[seed].content, slug, set(posts)) if slug in outgoing else []
            direction = 'both' if slug in incoming and slug in outgoing else ('in' if slug in incoming else 'out')
            entry = {'slug':slug, 'title':str(posts[slug].metadata.get('title', slug)),
                     'scope':posts[slug].metadata.get('scope', 'shared'),
                     'direction':direction,
                     'target_location':'anchored' if in_anchors else 'unknown',
                     'incoming_anchors':_anchor_summary(in_anchors),
                     'outgoing_anchors':_anchor_summary(out_anchors)}
            entry.update(_claim_list(grouped.get(slug, []),root,posts[slug].content,
                                     {i for i,_ in in_anchors} if in_anchors else None))
            neighbors.append(entry)
        seed_result = {'slug':seed,'title':str(posts[seed].metadata.get('title', seed)),
                       'scope':posts[seed].metadata.get('scope', 'shared')}
        seed_result.update(_claim_list(grouped.get(seed, []),root,posts[seed].content,None))
        return {'question':question, 'seed':seed_result, 'neighbors':neighbors,
                'graph_generated':generated,
                'pagination':{'total':len(ordered),'offset':offset,'limit':limit,
                              'returned':len(neighbors),'remaining':max(0,len(ordered)-offset-len(neighbors))}}
    except PreviewError:
        raise
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RecursionError, yaml.YAMLError):
        raise PreviewError('wiki_invalid') from None
