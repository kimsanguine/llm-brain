#!/usr/bin/env python3
"""Read-only claim binding and eligibility diagnostics; no statements in output."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from lib import claim_ledger


def audit(project_root: Path, *, show_pages: bool = False):
    root = Path(project_root)
    records = claim_ledger.read_claims_jsonl(root/'claims.jsonl')
    invalid = Counter()
    for record in records:
        try:
            claim_ledger.validate_claim_source_inventory([record], wiki_root=root/'wiki')
        except claim_ledger.ClaimSourceInventoryError:
            invalid[claim_ledger.claim_slug(record)] += 1
    result = {'records':len(records), 'invalid_pages':len(invalid),
              'invalid_records':sum(invalid.values()),
              'eligibility':dict(sorted(Counter(
                  claim_ledger.claim_exclusion_reason(r, project_root=root) or 'usable'
                  for r in records).items()))}
    if show_pages:
        result['pages'] = [{'slug': slug, 'invalid_records': count}
                           for slug, count in sorted(invalid.items())]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--show-pages', action='store_true', help='include private page slugs')
    args = parser.parse_args()
    print(json.dumps(audit(args.project_root, show_pages=args.show_pages), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
