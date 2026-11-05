"""Papers use the existing page, evidence, and redacted history contracts."""
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import claim_ledger
from lib.ontology_contract import load_action_catalog, load_ontology_contract
from lib.ontology_observations import observation_from_episode
from lib.ontology_projection import (OntologyProjectionError, build_private_bundle,
                                     canonical_bundle_json, explain_object, read_bundle)
from wiki_app.api import create_app
from wiki_app.pages import PageNotFound, find_page_path, load_page


STATEMENT = 'The synthetic study measured three samples.'


@pytest.fixture(params=['synthetic-study', 'lab/synthetic-study'])
def paper_project(tmp_path, request):
    root = tmp_path / 'project'
    slug = request.param
    source = root / 'raw/notes/study.md'
    source.parent.mkdir(parents=True)
    source.write_text(STATEMENT + '\n', encoding='utf-8')
    page = root / 'wiki/papers' / (slug + '.md')
    page.parent.mkdir(parents=True)
    page.write_text(
        '---\ntitle: Synthetic study\nupdated: 2026-11-01\n'
        'observation_expires: 2099-01-01\nsources: [raw/notes/study.md]\n---\n'
        + STATEMENT + '\n', encoding='utf-8')
    (root / 'index.md').write_text(
        '## papers/ (1)\n- [[' + slug + ']]: Synthetic study\n', encoding='utf-8')
    record = dict(claim_id='claim:' + slug + '-1', statement=STATEMENT, kind='fact',
                  raw_path='raw/notes/study.md',
                  raw_sha256=hashlib.sha256((STATEMENT + '\n').encode()).hexdigest(),
                  locator='raw/notes/study.md#L1-L1', valid_from='2026-11-01',
                  valid_until='2099-01-01', status='active', trust='trusted')
    (root / 'claims.jsonl').write_text(json.dumps(record) + '\n', encoding='utf-8')
    return root, slug


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def build(root):
    contract = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    return build_private_bundle(root, contract,
                                load_action_catalog(ROOT / 'schema/actions.yaml', contract))


def claims_cli(root, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/claims.py'), *args],
                          cwd=root, capture_output=True, text=True)


def context_data(text, prefix):
    return json.loads(next(line.removeprefix(prefix) for line in text.splitlines()
                           if line.startswith(prefix)))


def test_paper_lookup_and_page_api_are_read_only(paper_project):
    root, slug = paper_project
    before = snapshot(root)
    response = TestClient(create_app(wiki_root=root / 'wiki')).get('/api/page/' + slug)
    assert response.status_code == 200
    assert find_page_path(slug, root / 'wiki') == root / 'wiki/papers' / (slug + '.md')
    page = load_page(slug, root / 'wiki')
    assert page['category'] == 'papers'
    assert page['body_md'] == STATEMENT
    assert response.json()['slug'] == slug
    assert response.json()['title'] == 'Synthetic study'
    assert response.json()['category'] == 'papers'
    assert STATEMENT in response.json()['html']
    assert snapshot(root) == before


def test_single_source_paper_build_and_inventory_remain_usable(paper_project):
    root, slug = paper_project
    before = snapshot(root)
    records = claim_ledger.build_claim_ledger([slug], wiki_root=root / 'wiki', now=date(2026, 11, 5))
    assert [r.claim_id for r in records] == ['claim:' + slug + '-1']
    claim_ledger.validate_claim_source_inventory(records, wiki_root=root / 'wiki')
    trusted = context_data(claim_ledger.render_llm_context(records, project_root=root,
        now=date(2026, 11, 5)), 'TRUSTED_DATA_JSON=')
    assert [(r['statement'], r['raw_path']) for r in trusted] == [(STATEMENT, 'raw/notes/study.md')]
    assert snapshot(root) == before


def test_paper_cli_propose_build_context_keeps_explicit_sources_and_trust(paper_project):
    root, slug = paper_project
    capture = root / 'raw/captures/second.md'
    capture.parent.mkdir(parents=True)
    capture.write_text('An external capture reports four samples.\n', encoding='utf-8')
    page = root / 'wiki/papers' / (slug + '.md')
    page.write_text(page.read_text().replace('sources: [raw/notes/study.md]',
        'sources: [raw/notes/study.md, raw/captures/second.md]')
        + 'An external capture reports four samples.\n', encoding='utf-8')
    canonical_before = {name: snapshot(root / name) for name in ('raw', 'wiki')}
    proposed = claims_cli(root, 'propose', '--slug', slug)
    assert proposed.returncode == 0, proposed.stderr
    with pytest.raises(claim_ledger.ClaimLedgerError, match='exactly one'):
        claim_ledger.build_claim_ledger([slug], wiki_root=root / 'wiki')
    data = json.loads(proposed.stdout)
    assert data['unresolved'] == []
    assert [(m['claim_id'], m['raw_path'], m['source_binding']['quote']) for m in data['mappings']] == [
        ('claim:' + slug + '-1', 'raw/notes/study.md', STATEMENT),
        ('claim:' + slug + '-2', 'raw/captures/second.md', 'An external capture reports four samples.')]
    source_map = root / 'source-map.json'
    source_map.write_text(proposed.stdout, encoding='utf-8')
    result = claims_cli(root, 'build', '--slug', slug, '--source-map', str(source_map))
    assert result.returncode == 0, result.stderr
    records = claim_ledger.read_claims_jsonl(root / 'claims.jsonl')
    assert [r.trust for r in records] == ['trusted', 'untrusted']
    assert all(r.source_binding is not None for r in records)
    result = claims_cli(root, 'context', '--slug', slug)
    assert result.returncode == 0, result.stderr
    assert [r['claim_id'] for r in context_data(result.stdout, 'TRUSTED_DATA_JSON=')] == ['claim:' + slug + '-1']
    assert [r['claim_id'] for r in context_data(result.stdout, 'UNTRUSTED_DATA_JSON=')] == ['claim:' + slug + '-2']
    assert {name: snapshot(root / name) for name in ('raw', 'wiki')} == canonical_before


def test_paper_ontology_current_saved_and_api_explain_existing_object_types(paper_project, tmp_path):
    root, slug = paper_project
    before = snapshot(root)
    response = TestClient(create_app(wiki_root=root / 'wiki')).get('/api/ontology/page/' + slug)
    assert response.status_code == 200
    bundle = build(root)
    explanation = explain_object(bundle, 'page:' + slug).to_mapping()
    assert explanation['focus']['type'] == 'knowledge_page'
    assert explanation['claim_counts'] == dict(active=1, trusted=1, stale=0, superseded=0, untrusted=0)
    assert {obj['type'] for obj in explanation['objects']} == {'knowledge_page', 'claim', 'source'}
    assert [step['relation'] for step in explanation['incoming']] == ['compiled_into']
    saved = tmp_path / 'bundle.json'
    saved.write_text(canonical_bundle_json(bundle), encoding='utf-8')
    assert explain_object(read_bundle(saved), 'page:' + slug).to_mapping() == explanation
    assert response.json() == json.loads(json.dumps(explanation))
    assert snapshot(root) == before


@pytest.mark.parametrize('prefix,suffix', [('wiki/papers/', '.md'), ('papers/', '.md'),
                                         ('', ''), ('page:', '')])
def test_paper_episode_references_normalize_to_existing_page_identity(paper_project, prefix, suffix):
    _, slug = paper_project
    record = dict(timestamp='2026-11-01T00:00:00+00:00', task_type='ai_answer',
                  status='answered', read_pages=[prefix + slug + suffix])
    assert observation_from_episode(record).page_ids == ('page:' + slug,)


def test_paper_history_relations_retain_only_normalized_refs_and_no_prose(paper_project):
    root, slug = paper_project
    artifact = root / 'express/report/study.md'
    artifact.parent.mkdir(parents=True)
    artifact.write_text('PRIVATE ARTIFACT BODY', encoding='utf-8')
    episodes = root / 'episodes'
    episodes.mkdir()
    record = dict(timestamp='2026-11-01T00:00:00+00:00', task_type='express_report',
                  status='draft_ready', user_goal='PRIVATE GOAL', notes='PRIVATE NOTE',
                  inputs={'text': 'PRIVATE INPUT'}, outputs={'draft_path': 'express/report/study.md'},
                  read_pages=['wiki/papers/' + slug + '.md', 'papers/' + slug + '.md',
                              'page:' + slug, 'wiki/papers/../secret.md'])
    (episodes / '2026-11.jsonl').write_text(json.dumps(record) + '\n', encoding='utf-8')
    before = snapshot(root)
    bundle = build(root)
    assert bundle.observations[0]['page_ids'] == ('page:' + slug,)
    assert [(r.type, r.to_id) for r in bundle.relations if r.type == 'derived_from'] == [
        ('derived_from', 'page:' + slug)]
    assert 'PRIVATE' not in canonical_bundle_json(bundle)
    assert snapshot(root) == before


def test_paper_category_preserves_external_traversal_and_symlink_rejection(paper_project, tmp_path):
    root, _ = paper_project
    (root / 'secret.md').write_text('PRIVATE', encoding='utf-8')
    outside = tmp_path / 'outside.md'
    outside.write_text('PRIVATE', encoding='utf-8')
    (root / 'wiki/papers/escaped.md').symlink_to(outside)
    for slug in ('../../secret', str(outside.with_suffix('')), 'escaped'):
        with pytest.raises(PageNotFound):
            find_page_path(slug, root / 'wiki')
    with pytest.raises(OntologyProjectionError, match='input escapes project root'):
        build(root)


def test_paper_category_cannot_hide_duplicate_page_identity(paper_project):
    root, slug = paper_project
    duplicate = root / 'wiki/concepts' / (slug + '.md')
    duplicate.parent.mkdir(parents=True)
    duplicate.write_bytes((root / 'wiki/papers' / (slug + '.md')).read_bytes())
    with pytest.raises(OntologyProjectionError, match='ambiguous knowledge page identifier'):
        build(root)
