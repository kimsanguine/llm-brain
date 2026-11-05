"""Explicit bindings cannot launder a multi-source page into trusted claims."""
from dataclasses import replace
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lib import claim_ledger


def mixed_project(tmp_path):
    (tmp_path / 'wiki/concepts').mkdir(parents=True)
    (tmp_path / 'raw/notes').mkdir(parents=True)
    (tmp_path / 'raw/captures').mkdir(parents=True)
    (tmp_path / 'raw/notes/alpha.md').write_text('Alpha fact.\n', encoding='utf-8')
    (tmp_path / 'raw/captures/beta.md').write_text('Beta claim.\n', encoding='utf-8')
    (tmp_path / 'wiki/concepts/mixed.md').write_text(
        '---\ntitle: Mixed\nupdated: 2026-11-01\nsources:\n'
        '  - raw/notes/alpha.md\n  - raw/captures/beta.md\n---\n'
        'Alpha fact. Beta claim. Unmapped synthesis.\n', encoding='utf-8'
    )
    return tmp_path


def selection(root, index, statement, raw_path):
    return dict(
        claim_id=f'claim:mixed-{index}', raw_path=raw_path,
        raw_sha256=hashlib.sha256((root / raw_path).read_bytes()).hexdigest(),
        locator=raw_path + '#L1-L1',
        source_binding=dict(
            schema_version='llm-brain-claim-binding/0.1',
            page_sha256=hashlib.sha256((root / 'wiki/concepts/mixed.md').read_bytes()).hexdigest(),
            statement_sha256=hashlib.sha256(statement.encode()).hexdigest(),
            quote=statement,
        ),
    )


def build_bound(root, mapping):
    return claim_ledger.build_claim_ledger(
        ['mixed'], wiki_root=root / 'wiki', now=date(2026, 11, 5), source_map=mapping
    )


def test_explicit_sources_keep_each_claims_hash_and_trust(tmp_path):
    root = mixed_project(tmp_path)
    mappings = [selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md'),
                selection(root, 2, 'Beta claim.', 'raw/captures/beta.md')]
    records = build_bound(root, {m['claim_id']: m for m in mappings})
    assert [r.claim_id for r in records] == ['claim:mixed-1', 'claim:mixed-2']
    assert [r.trust for r in records] == ['trusted', 'untrusted']
    assert [r.raw_path for r in records] == ['raw/notes/alpha.md', 'raw/captures/beta.md']
    claim_ledger.validate_claim_source_inventory(records, wiki_root=root / 'wiki')
    assert claim_ledger.claim_exclusion_reason(records[0], project_root=root, now=date(2026, 11, 5)) is None
    assert claim_ledger.claim_exclusion_reason(records[1], project_root=root, now=date(2026, 11, 5)) == 'untrusted'
    path = root / 'claims.jsonl'
    claim_ledger.write_claims_jsonl(path, records, project_root=root)
    assert claim_ledger.read_claims_jsonl(path) == records
    assert records[0].to_mapping()['source_binding']['quote'] == 'Alpha fact.'


@pytest.mark.parametrize('damage', ['page_hash', 'raw_hash', 'statement_hash', 'quote', 'locator', 'unknown', 'source'])
def test_build_rejects_stale_or_forged_binding(tmp_path, damage):
    root = mixed_project(tmp_path)
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    if damage == 'page_hash':
        (root / 'wiki/concepts/mixed.md').write_text((root / 'wiki/concepts/mixed.md').read_text() + '\n')
    elif damage == 'raw_hash':
        (root / value['raw_path']).write_text('Changed.\n')
    elif damage == 'statement_hash':
        value['source_binding']['statement_sha256'] = '0' * 64
    elif damage == 'quote':
        value['source_binding']['quote'] = 'Another quote.'
    elif damage == 'locator':
        value['locator'] = value['raw_path'] + '#L2-L2'
    elif damage == 'unknown':
        value['source_binding']['approved'] = True
    else:
        (root / 'raw/notes/other.md').write_text('Alpha fact.\n')
        value['raw_path'] = 'raw/notes/other.md'
        value['locator'] = value['raw_path'] + '#L1-L1'
    with pytest.raises(claim_ledger.ClaimLedgerError):
        build_bound(root, {value['claim_id']: value})


def test_query_rechecks_page_and_exact_raw_line(tmp_path):
    root = mixed_project(tmp_path)
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    record = build_bound(root, {value['claim_id']: value})[0]
    forged = replace(record, locator=value['raw_path'] + '#L2-L2')
    assert claim_ledger.claim_exclusion_reason(forged, project_root=root, now=date(2026, 11, 5)) == 'source_binding_mismatch'
    with pytest.raises(claim_ledger.ClaimCitationError):
        claim_ledger.render_cited_answer('Answer [claim:mixed-1]', [forged], project_root=root, now=date(2026, 11, 5))
    page = root / 'wiki/concepts/mixed.md'
    page.write_text(page.read_text() + '\nUpdated page.\n')
    with pytest.raises(claim_ledger.ClaimSourceInventoryError):
        claim_ledger.validate_claim_source_inventory([record], wiki_root=root / 'wiki')
    assert claim_ledger.claim_exclusion_reason(record, project_root=root, now=date(2026, 11, 5)) == 'source_binding_mismatch'


def test_legacy_serialization_omits_binding_and_multi_source_still_fails(tmp_path):
    root = mixed_project(tmp_path)
    with pytest.raises(claim_ledger.ClaimLedgerError, match='exactly one'):
        claim_ledger.build_claim_ledger(['mixed'], wiki_root=root / 'wiki')
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    record = build_bound(root, {value['claim_id']: value})[0]
    legacy = replace(record, source_binding=None)
    assert 'source_binding' not in legacy.to_mapping()
    with pytest.raises(claim_ledger.ClaimSourceInventoryError):
        claim_ledger.validate_claim_source_inventory([legacy], wiki_root=root / 'wiki')


@pytest.mark.parametrize('damage', ['version', 'zero_line', 'range', 'null', 'unknown'])
def test_strict_binding_survives_persisted_ledger_boundary(tmp_path, damage):
    root = mixed_project(tmp_path)
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    record = build_bound(root, {value['claim_id']: value})[0].to_mapping()
    if damage == 'version':
        record['source_binding']['schema_version'] = 'future'
    elif damage == 'zero_line':
        record['locator'] = record['raw_path'] + '#L0-L0'
    elif damage == 'range':
        record['locator'] = record['raw_path'] + '#L2-L1'
    elif damage == 'null':
        record['source_binding'] = None
    else:
        record['source_binding']['unknown'] = 'x'
    ledger = root / 'claims.jsonl'
    ledger.write_text(json.dumps(record) + '\n')
    with pytest.raises(claim_ledger.ClaimLedgerError):
        claim_ledger.read_claims_jsonl(ledger)


def test_duplicate_json_fields_cannot_hide_a_conflicting_binding(tmp_path):
    root = mixed_project(tmp_path)
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    data = build_bound(root, {value['claim_id']: value})[0].to_mapping()
    text = json.dumps(data).replace('"quote": "Alpha fact."',
                                    '"quote": "Conflicting.", "quote": "Alpha fact."')
    ledger = root / 'claims.jsonl'
    ledger.write_text(text + '\n')
    with pytest.raises(claim_ledger.ClaimLedgerError):
        claim_ledger.read_claims_jsonl(ledger)


def test_valid_raw_quote_cannot_replace_the_current_wiki_statement(tmp_path):
    root = mixed_project(tmp_path)
    (root / 'raw/notes/alpha.md').write_text('Alpha fact.\nOther fact.\n')
    value = selection(root, 1, 'Alpha fact.', 'raw/notes/alpha.md')
    record = build_bound(root, {value['claim_id']: value})[0]
    binding = replace(record.source_binding, quote='Other fact.',
                      statement_sha256=hashlib.sha256(b'Other fact.').hexdigest())
    forged = replace(record, statement='Other fact.', source_binding=binding,
                     locator='raw/notes/alpha.md#L2-L2')
    with pytest.raises(claim_ledger.ClaimSourceInventoryError):
        claim_ledger.validate_claim_source_inventory([forged], wiki_root=root / 'wiki')
    assert claim_ledger.claim_exclusion_reason(forged, project_root=root, now=date(2026, 11, 5)) == 'source_binding_mismatch'
