"""Reject ambiguous or dangling executable descriptions before projecting data."""
import copy
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.ontology_contract import (OntologyContractError, load_ontology_contract, load_action_catalog)


def mapping(name):
    return yaml.safe_load((ROOT / 'schema' / name).read_text())


def test_loads_canonical_contracts():
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    catalog = load_action_catalog(ROOT / 'schema/actions.yaml', ontology)
    assert {t.id for t in ontology.object_types} == {'source', 'claim', 'knowledge_page', 'procedure', 'artifact'}
    assert {a.id for a in catalog.actions} == {'ingest', 'curate', 'query', 'express', 'share'}


@pytest.mark.parametrize('mutation', [
    lambda d: d.update(extra='SECRET'),
    lambda d: d['object_types'].append(copy.deepcopy(d['object_types'][0])),
    lambda d: d['relation_types'][0].update(from_type='missing'),
    lambda d: d['object_types'][0].update(id='bad-id'),
    lambda d: d['object_types'][0].update(required_attributes='not-a-list'),
    lambda d: d['relation_types'][0].update(extra=True),
])
def test_rejects_ambiguous_ontology(tmp_path, mutation):
    data = mapping('ontology.yaml')
    mutation(data)
    path = tmp_path / 'contract.yaml'
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(OntologyContractError):
        load_ontology_contract(path)


@pytest.mark.parametrize('changes', [
    {'inputs': ['missing']}, {'mode': 'execute'}, {'approval': 'auto'},
    {'mode': 'read', 'outputs': ['artifact']}, {'extra': 'SECRET'},
    {'evidence': [None]}, {'inputs': ['source', 'source']},
])
def test_rejects_invalid_actions(tmp_path, changes):
    data = mapping('actions.yaml')
    data['actions'][0].update(changes)
    path = tmp_path / 'actions.yaml'
    path.write_text(yaml.safe_dump(data))
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    with pytest.raises(OntologyContractError):
        load_action_catalog(path, ontology)


@pytest.mark.parametrize('text', ['schema_version: [SECRET', 'x: SECRET\nx: other\n', '- SECRET'])
def test_parser_errors_never_echo_content(tmp_path, text):
    path = tmp_path / 'contract.yaml'
    path.write_text(text)
    with pytest.raises(OntologyContractError) as error:
        load_ontology_contract(path)
    assert 'SECRET' not in str(error.value)


def test_missing_contract_has_safe_error(tmp_path):
    with pytest.raises(OntologyContractError) as error:
        load_ontology_contract(tmp_path / 'SECRET')
    assert 'SECRET' not in str(error.value)
