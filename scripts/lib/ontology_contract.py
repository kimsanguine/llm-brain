"""Strict declarative contracts for the local knowledge projection; no execution."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml


class OntologyContractError(ValueError):
    """A contract cannot safely describe the projection."""


@dataclass(frozen=True)
class ObjectTypeSpec:
    id: str
    required_attributes: tuple[str, ...]


@dataclass(frozen=True)
class RelationTypeSpec:
    id: str
    from_type: str
    to_type: str


@dataclass(frozen=True)
class ActionTypeSpec:
    id: str
    mode: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    approval: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class OntologyContract:
    schema_version: str
    object_types: tuple[ObjectTypeSpec, ...]
    relation_types: tuple[RelationTypeSpec, ...]


@dataclass(frozen=True)
class ActionCatalog:
    schema_version: str
    actions: tuple[ActionTypeSpec, ...]


class _StrictLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise OntologyContractError('contract keys must be unique strings')
        result[key] = loader.construct_object(value_node)
    return result


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)
_ID = re.compile(r'^[a-z][a-z0-9_]*$')


def fields(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise OntologyContractError('contract has missing or unknown fields')
    return value


def identifier(value):
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise OntologyContractError('invalid contract identifier')
    return value


def identifiers(value):
    if not isinstance(value, list):
        raise OntologyContractError('expected identifier list')
    items = tuple(identifier(item) for item in value)
    if len(items) != len(set(items)):
        raise OntologyContractError('duplicate identifier')
    return items


def _load(path):
    try:
        return yaml.load(Path(path).read_text(encoding='utf-8'), Loader=_StrictLoader)
    except (OSError, UnicodeError, yaml.YAMLError, RecursionError, TypeError, ValueError) as exc:
        raise OntologyContractError('contract cannot be read or parsed') from exc


def _items(value):
    if not isinstance(value, list):
        raise OntologyContractError('expected contract item list')
    return value


def _unique(items):
    if len({item.id for item in items}) != len(items):
        raise OntologyContractError('duplicate contract id')
    return tuple(items)


def load_ontology_contract(path: Path) -> OntologyContract:
    data = fields(_load(path), ('schema_version', 'object_types', 'relation_types'))
    if data['schema_version'] != 'llm-brain-ontology/0.1':
        raise OntologyContractError('unsupported ontology schema version')
    types = []
    for raw in _items(data['object_types']):
        fields(raw, ('id', 'required_attributes'))
        types.append(ObjectTypeSpec(identifier(raw['id']), identifiers(raw['required_attributes'])))
    _unique(types)
    type_ids = {t.id for t in types}
    relations = []
    for raw in _items(data['relation_types']):
        fields(raw, ('id', 'from_type', 'to_type'))
        spec = RelationTypeSpec(*(identifier(raw[key]) for key in ('id', 'from_type', 'to_type')))
        if spec.from_type not in type_ids or spec.to_type not in type_ids:
            raise OntologyContractError('unknown relation endpoint type')
        relations.append(spec)
    return OntologyContract(data['schema_version'], tuple(types), _unique(relations))


def action_from_mapping(raw, ontology: OntologyContract) -> ActionTypeSpec:
    fields(raw, ('id', 'mode', 'inputs', 'outputs', 'approval', 'evidence'))
    spec = ActionTypeSpec(identifier(raw['id']), identifier(raw['mode']),
                          identifiers(raw['inputs']), identifiers(raw['outputs']),
                          identifier(raw['approval']), identifiers(raw['evidence']))
    if spec.mode not in {'read', 'write', 'publish'}:
        raise OntologyContractError('invalid action mode')
    if spec.approval not in {'none', 'explicit_invocation', 'exact_share_phrase'}:
        raise OntologyContractError('invalid action approval')
    if spec.mode == 'read' and spec.outputs:
        raise OntologyContractError('read action cannot declare object outputs')
    if not set(spec.inputs + spec.outputs) <= {t.id for t in ontology.object_types}:
        raise OntologyContractError('unknown action object type')
    return spec


def load_action_catalog(path: Path, ontology: OntologyContract) -> ActionCatalog:
    data = fields(_load(path), ('schema_version', 'actions'))
    if data['schema_version'] != 'llm-brain-actions/0.1':
        raise OntologyContractError('unsupported action schema version')
    return ActionCatalog(data['schema_version'], _unique([
        action_from_mapping(raw, ontology) for raw in _items(data['actions'])
    ]))
