"""Preview must expose evidence and uncertainty without changing data or calling a model."""
import hashlib
import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_graph
from wiki_app import api
from tests.test_ontology_projection import snapshot


def _graph(root, monkeypatch):
    monkeypatch.setattr(export_graph, 'WIKI_DIR', root / 'wiki')
    monkeypatch.setattr(export_graph, 'OUTPUT', root / 'wiki/graph.json')
    assert export_graph.main() == 0


def _project(root, monkeypatch):
    alpha = root / 'wiki/concepts/alpha.md'
    alpha.write_text(alpha.read_text() + '\n[[beta]]\n')
    (root / 'wiki/concepts/beta.md').write_text(
        '---\ntitle: Beta\nsources: [raw/notes/beta.md]\n---\n'
        'Beta is independent evidence. [[alpha]]\n')
    raw = b'Beta is independent evidence.\n'
    (root / 'raw/notes/beta.md').write_bytes(raw)
    record = dict(claim_id='claim:beta-1', statement=raw.decode().strip(), kind='fact',
                  raw_path='raw/notes/beta.md', raw_sha256=hashlib.sha256(raw).hexdigest(),
                  valid_from='2026-01-01', valid_until='2099-01-01', status='active', trust='trusted')
    with (root / 'claims.jsonl').open('a') as f:
        f.write(json.dumps(record) + '\n')
    _graph(root, monkeypatch)


def _request(client, **updates):
    body = {'seed_slug':'alpha', 'question':'Where is the evidence?'}
    body.update(updates)
    return client.post('/api/graph-context/preview', json=body)


def test_preview_exposes_link_paths_claim_provenance_and_is_read_only(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    monkeypatch.setattr(api.llm_client, 'call_llm', lambda *a, **k: (_ for _ in ()).throw(AssertionError('model called')))
    before = snapshot(ontology_project)
    data = _request(TestClient(api.create_app(wiki_root=ontology_project/'wiki'))).json()
    assert data['seed']['slug'] == 'alpha'
    assert data['question'] == 'Where is the evidence?'
    assert data['pagination']['total'] == 1
    neighbor = data['neighbors'][0]
    assert neighbor['slug'] == 'beta' and neighbor['direction'] == 'both'
    assert neighbor['incoming_anchors']['total'] == 1
    assert neighbor['outgoing_anchors']['total'] == 1
    claim = neighbor['claims'][0]
    assert claim['id'] == 'claim:beta-1'
    assert claim['eligibility'] == 'usable'
    assert claim['source']['raw_path'] == 'raw/notes/beta.md'
    assert claim['link_context'] == 'same_paragraph'
    assert snapshot(ontology_project) == before


def test_invalid_unrelated_claim_is_visible_but_not_authorized(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    beta = ontology_project/'wiki/concepts/beta.md'
    beta.write_text(beta.read_text().replace('raw/notes/beta.md', 'raw/notes/alpha.md'))
    response = _request(TestClient(api.create_app(wiki_root=ontology_project/'wiki')))
    assert response.status_code == 200
    claim = response.json()['neighbors'][0]['claims'][0]
    assert claim['eligibility'] == 'inventory_invalid'
    assert response.json()['seed']['claims'][0]['eligibility'] == 'usable'


def test_malformed_or_missing_ledger_is_not_reported_as_empty_success(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    ledger = ontology_project/'claims.jsonl'
    ledger.write_text('{PRIVATE broken')
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'ledger_invalid'
    assert 'PRIVATE' not in response.text
    ledger.unlink()
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'ledger_missing'


def test_stale_graph_and_missing_graph_fail_without_auto_rebuild(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    beta = ontology_project/'wiki/concepts/beta.md'
    beta.write_text(beta.read_text().replace('[[alpha]]', 'unlinked'))
    before = snapshot(ontology_project)
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'graph_stale'
    assert snapshot(ontology_project) == before
    (ontology_project/'wiki/graph.json').unlink()
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'graph_missing'


def test_outgoing_only_location_is_unknown_and_pagination_is_explicit(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    (ontology_project/'wiki/concepts/gamma.md').write_text('---\ntitle: Gamma\n---\nGamma page.\n')
    alpha = ontology_project/'wiki/concepts/alpha.md'
    alpha.write_text(alpha.read_text() + '\n[[gamma]]\n')
    _graph(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    first = _request(client, limit=1, offset=0).json()
    assert first['pagination'] == {'total':2, 'offset':0, 'limit':1, 'returned':1, 'remaining':1}
    second = _request(client, limit=1, offset=1).json()
    assert second['neighbors'][0]['slug'] == 'gamma'
    assert second['neighbors'][0]['direction'] == 'out'
    assert second['neighbors'][0]['target_location'] == 'unknown'
    assert second['pagination']['remaining'] == 0


def test_invalid_selected_claim_blocks_without_disclosing_it(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    alpha = ontology_project/'wiki/concepts/alpha.md'
    alpha.write_text(alpha.read_text().replace('raw/notes/alpha.md', 'raw/notes/beta.md'))
    response = _request(TestClient(api.create_app(wiki_root=ontology_project/'wiki')))
    assert response.status_code == 409 and response.json()['code'] == 'seed_inventory_invalid'
    assert 'Alpha is a synthetic knowledge example.' not in response.text


def test_graph_and_ledger_symlinks_cannot_escape_project(ontology_project, monkeypatch, tmp_path):
    _project(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    graph = ontology_project/'wiki/graph.json'
    outside_graph = tmp_path/'outside-graph.json'
    outside_graph.write_bytes(graph.read_bytes())
    graph.unlink()
    graph.symlink_to(outside_graph)
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'graph_invalid'
    graph.unlink()
    graph.write_bytes(outside_graph.read_bytes())
    ledger = ontology_project/'claims.jsonl'
    outside_ledger = tmp_path/'outside-ledger.jsonl'
    outside_ledger.write_bytes(ledger.read_bytes())
    ledger.unlink()
    ledger.symlink_to(outside_ledger)
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'ledger_invalid'


def test_changed_raw_source_is_not_mislabeled_usable(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    (ontology_project/'raw/notes/beta.md').write_text('Changed source.\n')
    response = _request(TestClient(api.create_app(wiki_root=ontology_project/'wiki')))
    assert response.status_code == 200
    assert response.json()['neighbors'][0]['claims'][0]['eligibility'] == 'source_hash_mismatch'


def test_malformed_wiki_metadata_returns_safe_failure(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    (ontology_project/'wiki/concepts/beta.md').write_text('---\ntitle: [SECRET\n---\n')
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'wiki_invalid'
    assert 'SECRET' not in response.text


def test_wiki_page_cannot_be_a_symlink_to_raw(ontology_project, monkeypatch):
    _project(ontology_project, monkeypatch)
    client = TestClient(api.create_app(wiki_root=ontology_project/'wiki'))
    beta = ontology_project/'wiki/concepts/beta.md'
    target = ontology_project/'raw/notes/beta.md'
    target.write_bytes(beta.read_bytes())
    beta.unlink()
    beta.symlink_to(target)
    response = _request(client)
    assert response.status_code == 409 and response.json()['code'] == 'wiki_invalid'
