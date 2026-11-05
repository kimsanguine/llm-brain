"""The local explanation endpoint is read-only and returns safe recovery states."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wiki_app.api import create_app
from tests.test_ontology_projection import snapshot


def test_provenance_endpoint_and_open_panel_do_not_write(ontology_project):
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    before = snapshot(ontology_project)
    response = client.get('/api/ontology/page/alpha')
    assert response.status_code == 200
    data = response.json()
    assert data['focus']['id'] == 'page:alpha'
    assert [s['relation'] for s in data['incoming']] == ['compiled_into']
    assert any(o['attributes'].get('relative_path') == 'raw/notes/alpha.md' for o in data['objects'])
    assert 'PRIVATE PROCEDURE BODY' not in response.text
    assert snapshot(ontology_project) == before


def test_safe_missing_and_invalid_inventory_responses(ontology_project):
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    response = client.get('/api/ontology/page/missing')
    assert response.status_code == 404
    assert response.json() == {'detail': 'ontology object not found'}
    (ontology_project / 'claims.jsonl').write_text('{SECRET')
    response = client.get('/api/ontology/page/alpha')
    assert response.status_code == 409
    assert response.json() == {'detail': 'ontology inventory invalid', 'recovery': 'uv run python scripts/claims.py build --help'}
    assert 'SECRET' not in response.text and str(ontology_project) not in response.text


@pytest.mark.parametrize('slug', ['alpha%5Csecret', 'alpha%2F..%2Fsecret', 'bad%20slug'])
def test_unsafe_slugs_are_rejected(ontology_project, slug):
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    assert client.get('/api/ontology/page/' + slug).status_code == 422


def test_nested_page_slugs_are_supported(ontology_project):
    directory = ontology_project / 'wiki/projects/team'
    directory.mkdir(parents=True)
    (directory / 'topic.md').write_text('---\ntitle: Team topic\n---\n')
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    response = client.get('/api/ontology/page/team%2Ftopic')
    assert response.status_code == 200
    assert response.json()['claim_counts']['active'] == 0


def test_frontend_has_accessible_panel_and_text_node_rendering():
    root = Path(__file__).resolve().parents[1] / 'wiki_app/static'
    html = (root / 'index.html').read_text()
    js = (root / 'app.js').read_text()
    assert 'id="ontology-explain-toggle"' in html
    assert 'id="ontology-explain-panel" hidden' in html
    assert '/api/ontology/page/${encodeURIComponent(slug)}' in js
    renderer = js.split('function renderOntologyExplanation(')[1].split('// ---')[0]
    assert '.textContent' in renderer and '.innerHTML' not in renderer


def test_inventory_recovery_command_runs_read_only_help(ontology_project):
    import shlex
    import subprocess
    import sys
    root = Path(__file__).resolve().parents[1]
    client = TestClient(create_app(wiki_root=ontology_project / 'wiki'))
    (ontology_project / 'claims.jsonl').write_text('{broken')
    data = client.get('/api/ontology/page/alpha').json()
    parts = shlex.split(data['recovery'])
    assert parts[:3] == ['uv', 'run', 'python']
    before = snapshot(ontology_project)
    result = subprocess.run([sys.executable, '-B', str(root / parts[3]), *parts[4:]],
                            capture_output=True, text=True, cwd=ontology_project)
    assert result.returncode == 0, result.stderr
    assert '--slug' in result.stdout
    assert snapshot(ontology_project) == before


def test_multi_source_endpoint_explains_each_explicit_source_without_writes(tmp_path):
    from tests.test_claim_source_binding import mixed_project
    from lib import claim_ledger, claim_source_map
    root = mixed_project(tmp_path)
    proposed = claim_source_map.propose_source_map(['mixed'], wiki_root=root / 'wiki')
    records = claim_ledger.build_claim_ledger(['mixed'], wiki_root=root / 'wiki',
        source_map={m['claim_id']: m for m in proposed['mappings']})
    claim_ledger.write_claims_jsonl(root / 'claims.jsonl', records, project_root=root)
    before = snapshot(root)
    client = TestClient(create_app(wiki_root=root / 'wiki'))
    response = client.get('/api/ontology/page/mixed')
    assert response.status_code == 200
    data = response.json()
    claims = [o for o in data['objects'] if o['type'] == 'claim']
    assert {o['attributes']['raw_path'] for o in claims} == {'raw/notes/alpha.md', 'raw/captures/beta.md'}
    assert {o['attributes']['trust'] for o in claims} == {'trusted', 'untrusted'}
    assert all('source_binding' in o['attributes'] for o in claims)
    assert snapshot(root) == before
