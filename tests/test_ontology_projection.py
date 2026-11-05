"""A projection preserves provenance and never authorizes corrupt inventories."""
from pathlib import Path
import hashlib
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.ontology_contract import load_ontology_contract, load_action_catalog
from lib.ontology_projection import (build_private_bundle, canonical_bundle_json, OntologyProjectionError)


def build(root):
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    return build_private_bundle(root, ontology, load_action_catalog(ROOT / 'schema/actions.yaml', ontology))


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_projects_real_ledger_and_preserves_source_claim_page(ontology_project):
    before = snapshot(ontology_project)
    bundle = build(ontology_project)
    objects = {obj.id: obj for obj in bundle.objects}
    sha = hashlib.sha256(b'Alpha is a synthetic knowledge example.\n').hexdigest()
    assert objects['source:' + sha].attributes == {'sha256': sha, 'relative_path': 'raw/notes/alpha.md'}
    assert objects['claim:alpha-1'].attributes['statement'] == 'Alpha is a synthetic knowledge example.'
    assert objects['page:alpha'].attributes == {'slug': 'alpha', 'title': 'Alpha', 'scope': 'shared', 'updated': '2026-01-01'}
    assert {(r.type, r.from_id, r.to_id) for r in bundle.relations} == {
        ('supports', 'source:' + sha, 'claim:alpha-1'),
        ('compiled_into', 'claim:alpha-1', 'page:alpha'),
    }
    assert 'PRIVATE PROCEDURE BODY' not in canonical_bundle_json(bundle)
    assert before == snapshot(ontology_project)


def test_determinism_and_existing_only_wikilinks(ontology_project):
    path = ontology_project / 'wiki/concepts/alpha.md'
    path.write_text(path.read_text() + '\n[[beta|Beta]] [[missing]]\n')
    (ontology_project / 'wiki/concepts/beta.md').write_text('---\ntitle: Beta\n---\n')
    first = canonical_bundle_json(build(ontology_project))
    assert first == canonical_bundle_json(build(ontology_project))
    links = [r for r in build(ontology_project).relations if r.type == 'links_to']
    assert [(r.from_id, r.to_id) for r in links] == [('page:alpha', 'page:beta')]
    assert len(json.loads(first)['source_fingerprint']) == 64
    assert 'generated_at' not in first


@pytest.mark.parametrize('damage', ['corrupt', 'missing', 'empty', 'source_changed', 'orphan_claim'])
def test_invalid_inventory_fails_closed_without_echoing_data(ontology_project, damage):
    ledger = ontology_project / 'claims.jsonl'
    if damage == 'corrupt':
        ledger.write_text('{SECRET')
    elif damage == 'missing':
        ledger.unlink()
    elif damage == 'empty':
        ledger.write_text('')
    elif damage == 'source_changed':
        p = ontology_project / 'wiki/concepts/alpha.md'
        p.write_text(p.read_text().replace('raw/notes/alpha.md', 'raw/notes/other.md'))
    else:
        (ontology_project / 'wiki/concepts/alpha.md').unlink()
    with pytest.raises(OntologyProjectionError) as error:
        build(ontology_project)
    assert 'SECRET' not in str(error.value)


def test_fresh_clone_can_validate_without_personal_data(tmp_path):
    bundle = build(tmp_path)
    assert bundle.objects == ()
    assert bundle.counts['action_type_count'] == 5


def test_duplicate_page_ids_and_symlink_sources_fail_closed(ontology_project, tmp_path):
    path = ontology_project / 'wiki/tools'
    path.mkdir()
    (path / 'alpha.md').write_text('---\ntitle: Conflicting alpha\n---\n')
    with pytest.raises(OntologyProjectionError):
        build(ontology_project)
    (path / 'alpha.md').unlink()
    source = ontology_project / 'raw/notes/alpha.md'
    source.unlink()
    outside = tmp_path / 'SECRET'
    outside.write_text('SECRET')
    source.symlink_to(outside)
    with pytest.raises(OntologyProjectionError):
        build(ontology_project)

