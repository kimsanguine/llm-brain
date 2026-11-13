"""A changed unrelated page must not disable safe evidence on other pages."""
import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from wiki_app.api import _collect_context, create_app
from lib import claim_ledger
from scripts.claims_audit import audit


def add_beta(root):
    raw = b'Beta is independently supported.\n'
    (root / 'raw/notes/beta.md').write_bytes(raw)
    (root / 'wiki/concepts/beta.md').write_text(
        '---\ntitle: Beta\nsources: [raw/notes/beta.md]\n---\n'
        'Beta is independently supported.\n', encoding='utf-8')
    record = dict(claim_id='claim:beta-1', statement=raw.decode().strip(), kind='fact',
                  raw_path='raw/notes/beta.md', raw_sha256=hashlib.sha256(raw).hexdigest(),
                  valid_from='2026-01-01', valid_until='2099-01-01',
                  status='active', trust='trusted')
    with (root / 'claims.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')
    # Legacy alpha now points elsewhere. Its claim must remain unusable.
    path = root / 'wiki/concepts/alpha.md'
    path.write_text(path.read_text().replace('raw/notes/alpha.md', 'raw/notes/beta.md'))


def test_unrelated_invalid_page_does_not_break_valid_page_but_bad_page_is_blocked(ontology_project):
    add_beta(ontology_project)
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    good = client.get('/api/ontology/page/beta')
    assert good.status_code == 200
    assert any(item['id'] == 'claim:beta-1' for item in good.json()['objects'])
    assert client.get('/api/ontology/page/alpha').status_code == 409


def test_ai_context_checks_only_requested_pages_without_accepting_invalid_claim(ontology_project):
    add_beta(ontology_project)
    context, slugs, ledger = _collect_context(['beta'], ontology_project / 'wiki')
    assert slugs == ['beta']
    assert [record.claim_id for record in ledger] == ['claim:beta-1']
    assert 'Beta is independently supported.' in context
    with pytest.raises(claim_ledger.ClaimSourceInventoryError):
        _collect_context(['alpha'], ontology_project / 'wiki')


def test_malformed_unrelated_ledger_record_still_fails_closed(ontology_project):
    add_beta(ontology_project)
    with (ontology_project / 'claims.jsonl').open('a') as f:
        f.write('{broken json\n')
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    assert client.get('/api/ontology/page/beta').status_code == 409
    with pytest.raises(claim_ledger.ClaimLedgerError):
        _collect_context(['beta'], ontology_project / 'wiki')


def test_audit_reports_drift_without_exposing_statements_or_writing(ontology_project):
    add_beta(ontology_project)
    ledger = ontology_project / 'claims.jsonl'
    before = ledger.read_bytes()
    report = audit(ontology_project)
    assert report['records'] == 2
    assert report['invalid_pages'] == 1
    assert report['invalid_records'] == 1
    assert 'pages' not in report
    assert 'synthetic knowledge example' not in str(report)
    assert ledger.read_bytes() == before
    assert audit(ontology_project, show_pages=True)['pages'][0]['slug'] == 'alpha'
