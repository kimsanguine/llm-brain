"""Saved bundles receive the same strict checks as current projections."""
import copy
import json

import pytest

from tests.test_ontology_projection import build
from lib.ontology_projection import (explain_object, read_bundle, canonical_bundle_json,
                                     OntologyProjectionError, OntologyObjectNotFound)


def test_explain_claim_and_page_follow_full_provenance_chain(ontology_project):
    bundle = build(ontology_project)
    claim = explain_object(bundle, 'claim:alpha-1')
    assert claim.focus.id == 'claim:alpha-1'
    assert [s.relation for s in claim.incoming] == ['supports']
    assert [s.relation for s in claim.outgoing] == ['compiled_into']
    page = explain_object(bundle, 'page:alpha').to_mapping()
    assert page['focus']['attributes']['title'] == 'Alpha'
    assert any(o['type'] == 'source' for o in page['objects'])
    assert page['claim_counts'] == dict(active=1, trusted=1, stale=0, superseded=0, untrusted=0)


def test_unknown_id_has_no_path_suggestions(ontology_project):
    with pytest.raises(OntologyObjectNotFound, match='unknown object id'):
        explain_object(build(ontology_project), 'page:SECRET')


def test_saved_bundle_round_trip(tmp_path, ontology_project):
    bundle = build(ontology_project)
    path = tmp_path / 'bundle.json'
    path.write_text(canonical_bundle_json(bundle))
    assert canonical_bundle_json(read_bundle(path)) == canonical_bundle_json(bundle)


@pytest.mark.parametrize('mutation', [
    lambda d: d.update(extra='SECRET'),
    lambda d: d['objects'][0].update(extra='SECRET'),
    lambda d: d['objects'].append(copy.deepcopy(d['objects'][0])),
    lambda d: d['objects'][0]['attributes'].update(extra='SECRET'),
    lambda d: d['relations'][0].update(to_id='page:missing'),
    lambda d: d['relations'][0].update(type='unknown'),
    lambda d: d['relations'][0].update(evidence_ids=['observation:0000000000000000']),
    lambda d: d['action_types'][0].update(inputs=['missing']),
    lambda d: d['counts'].update(object_count=-1),
    lambda d: d.update(source_fingerprint='0'*64),
    lambda d: d['objects'][0]['attributes'].update(status='bad'),
])
def test_rejects_tampered_saved_bundles(tmp_path, ontology_project, mutation):
    data = build(ontology_project).to_mapping()
    mutation(data)
    path = tmp_path / 'bundle.json'
    path.write_text(json.dumps(data))
    with pytest.raises(OntologyProjectionError) as error:
        read_bundle(path)
    assert 'SECRET' not in str(error.value)


def test_policy_notes_preserve_untrusted_and_private_meanings(ontology_project):
    path = ontology_project / 'claims.jsonl'
    path.write_text(path.read_text().replace('"trusted"', '"untrusted"').replace('"active"', '"stale"'))
    path = ontology_project / 'wiki/concepts/alpha.md'
    path.write_text(path.read_text().replace('title: Alpha', 'title: Alpha\nscope: private'))
    bundle = build(ontology_project)
    assert set(explain_object(bundle, 'claim:alpha-1').policy_notes) == {'claim is stale', 'claim is untrusted'}
    assert 'page scope is private' in explain_object(bundle, 'page:alpha').policy_notes


@pytest.mark.parametrize('mutation', [
    lambda d: d['objects'][0]['attributes'].update(trust='automatic'),
    lambda d: d['relations'][0].update(to_id='page:missing'),
    lambda d: d['objects'][-1]['attributes'].update(relative_path='/Users/SECRET'),
    lambda d: d['action_types'][0].update(extra='SECRET'),
])
def test_strict_validation_is_independent_of_fingerprint(tmp_path, ontology_project, mutation):
    import hashlib
    data = build(ontology_project).to_mapping()
    mutation(data)
    payload = {key: data[key] for key in ('objects', 'relations', 'action_types', 'observations')}
    data['source_fingerprint'] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    path = tmp_path / 'bundle.json'
    path.write_text(json.dumps(data))
    with pytest.raises(OntologyProjectionError):
        read_bundle(path)


@pytest.mark.parametrize('edge', ['supports', 'compiled_into'])
def test_saved_bundle_cannot_reassign_a_claim_to_another_source_or_page(tmp_path, ontology_project, edge):
    import hashlib
    data = build(ontology_project).to_mapping()
    if edge == 'supports':
        source = next(o for o in data['objects'] if o['type'] == 'source')
        source['id'] = 'source:' + '0' * 64
        source['attributes']['sha256'] = '0' * 64
        next(r for r in data['relations'] if r['type'] == edge)['from_id'] = source['id']
    else:
        page = next(o for o in data['objects'] if o['type'] == 'knowledge_page')
        page['id'], page['attributes']['slug'] = 'page:beta', 'beta'
        next(r for r in data['relations'] if r['type'] == edge)['to_id'] = page['id']
    payload = {key: data[key] for key in ('objects', 'relations', 'action_types', 'observations')}
    data['source_fingerprint'] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    path = tmp_path / 'bundle.json'
    path.write_text(json.dumps(data))
    with pytest.raises(OntologyProjectionError):
        read_bundle(path)
