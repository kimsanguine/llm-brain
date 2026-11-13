#!/usr/bin/env python3
"""Compare two private claim ledgers without changing either ledger."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from lib.claim_ledger import read_claims_jsonl


def _identity(record):
    return (record.statement, record.raw_path, record.raw_sha256)


def compare(before, after):
    old = {r.claim_id: r for r in before}
    new = {r.claim_id: r for r in after}
    pairs = []
    # Exact ID and evidence first. ID alone can refer to a different sentence
    # after a wiki edit, so it must not hide a moved original sentence.
    for key in sorted(old.keys() & new.keys()):
        if _identity(old[key]) == _identity(new[key]):
            pairs.append((old.pop(key), new.pop(key), 'same_id'))
    old_identity, new_identity = defaultdict(list), defaultdict(list)
    for value in old.values(): old_identity[_identity(value)].append(value)
    for value in new.values(): new_identity[_identity(value)].append(value)
    for identity in old_identity.keys() & new_identity.keys():
        a, b = old_identity[identity], new_identity[identity]
        if len(a) == len(b) == 1:
            pairs.append((old.pop(a[0].claim_id), new.pop(b[0].claim_id), 'moved_id'))
    for key in sorted(old.keys() & new.keys()):
        pairs.append((old.pop(key), new.pop(key), 'id_reused_or_evidence_changed'))

    changes = []
    for a, b, match in pairs:
        fields = [key for key in ('statement', 'raw_path', 'raw_sha256', 'locator',
                  'kind', 'status', 'trust', 'valid_from', 'valid_until', 'source_binding')
                  if getattr(a, key) != getattr(b, key)]
        if fields or a.claim_id != b.claim_id:
            changes.append({'old_id': a.claim_id, 'new_id': b.claim_id,
                            'match': match, 'changed_fields': fields,
                            'old_trust': a.trust, 'new_trust': b.trust})
    return {'changes': sorted(changes, key=lambda x: x['old_id']),
            'removed_ids': sorted(old), 'added_ids': sorted(new),
            'before_count': len(before), 'after_count': len(after)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare(read_claims_jsonl(args.before), read_claims_jsonl(args.after)),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
