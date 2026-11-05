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


def test_public_example_matches_synthetic_projection(ontology_project):
    expected = canonical_bundle_json(build(ontology_project))
    committed = (ROOT / 'examples/ontology-bundle-example.json').read_text(encoding='utf-8')
    assert committed == expected
    data = json.loads(committed)
    assert '/Users/' not in committed and '/home/' not in committed
    # inputs/outputs are legitimate action-schema keys; raw/notes is a required synthetic path.
    # Privacy assertions apply to observations and prose, not substrings in those schema fields.
    for observation in data['observations']:
        assert not {'user_goal', 'inputs', 'outputs', 'notes'} & observation.keys()
    assert 'PRIVATE PROCEDURE BODY' not in committed


def test_bound_multi_source_claims_round_trip_without_losing_evidence(tmp_path):
    from tests.test_claim_source_binding import mixed_project
    from lib import claim_ledger, claim_source_map
    from lib.ontology_projection import validate_bundle_mapping
    root = mixed_project(tmp_path)
    proposal = claim_source_map.propose_source_map(['mixed'], wiki_root=root / 'wiki')
    records = claim_ledger.build_claim_ledger(['mixed'], wiki_root=root / 'wiki',
        source_map={m['claim_id']: m for m in proposal['mappings']})
    claim_ledger.write_claims_jsonl(root / 'claims.jsonl', records, project_root=root)
    bundle = build(root)
    text = canonical_bundle_json(bundle)
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    assert canonical_bundle_json(validate_bundle_mapping(json.loads(text), ontology)) == text
    assert len([r for r in bundle.relations if r.type == 'supports']) == 2
    bound = next(o for o in bundle.objects if o.id == 'claim:mixed-1')
    assert bound.attributes['source_binding']['quote'] == 'Alpha fact.'
    with pytest.raises(TypeError):
        bound.attributes['source_binding']['quote'] = 'Changed.'
    damaged = json.loads(text)
    claim = next(o for o in damaged['objects'] if o['id'] == 'claim:mixed-1')
    claim['attributes']['source_binding']['unknown'] = 'bad'
    with pytest.raises(OntologyProjectionError):
        validate_bundle_mapping(damaged, ontology)


def alias_project(root):
    from lib import claim_ledger
    alias = root / 'raw/captures/copy.md'
    alias.parent.mkdir(parents=True)
    alias.write_bytes((root / 'raw/notes/alpha.md').read_bytes())
    (root / 'wiki/concepts/beta.md').write_text(
        '---\ntitle: Beta\nsources: [raw/captures/copy.md]\nupdated: 2026-01-01\n---\n'
        'Alpha is a synthetic knowledge example.\n')
    records = claim_ledger.build_claim_ledger(['alpha', 'beta'], wiki_root=root / 'wiki')
    claim_ledger.write_claims_jsonl(root / 'claims.jsonl', records, project_root=root)
    return root


def test_identical_raw_bytes_at_two_paths_share_identity_and_keep_each_claim_path(ontology_project):
    from lib.ontology_projection import validate_bundle_mapping
    root = alias_project(ontology_project)
    bundle = build(root)
    sources = [o for o in bundle.objects if o.type == 'source']
    assert len(sources) == 1
    assert sources[0].attributes['relative_path'] == 'raw/captures/copy.md'
    assert sources[0].attributes['relative_paths'] == ('raw/captures/copy.md', 'raw/notes/alpha.md')
    claims = {o.id: o for o in bundle.objects if o.type == 'claim'}
    assert claims['claim:alpha-1'].attributes['raw_path'] == 'raw/notes/alpha.md'
    assert claims['claim:alpha-1'].attributes['trust'] == 'trusted'
    assert claims['claim:beta-1'].attributes['trust'] == 'untrusted'
    text = canonical_bundle_json(bundle)
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    assert canonical_bundle_json(validate_bundle_mapping(json.loads(text), ontology)) == text
    assert len([r for r in bundle.relations if r.type == 'supports']) == 2


@pytest.mark.parametrize('paths', [[], ['raw/notes/alpha.md'],
    ['raw/notes/alpha.md', 'raw/captures/copy.md'],
    ['raw/captures/copy.md', 'raw/captures/copy.md'],
    ['raw/../secret', 'raw/notes/alpha.md'], 'raw/notes/alpha.md'])
def test_saved_source_aliases_are_strict_even_with_recomputed_fingerprint(ontology_project, paths):
    from lib.ontology_projection import validate_bundle_mapping
    data = json.loads(canonical_bundle_json(build(alias_project(ontology_project))))
    source = next(o for o in data['objects'] if o['type'] == 'source')
    source['attributes']['relative_paths'] = paths
    payload = {key: data[key] for key in ('objects', 'relations', 'action_types', 'observations')}
    data['source_fingerprint'] = hashlib.sha256(json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    with pytest.raises(OntologyProjectionError):
        validate_bundle_mapping(data, load_ontology_contract(ROOT / 'schema/ontology.yaml'))
