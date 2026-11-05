"""Deterministic, read-only projection of canonical file-first knowledge assets."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from types import MappingProxyType
from typing import Mapping

import frontmatter
import yaml

from lib import claim_ledger
from lib.ontology_contract import OntologyContract, ActionCatalog, ActionTypeSpec


class OntologyProjectionError(ValueError):
    """Safe aggregate diagnostic, without personal statements or paths."""


@dataclass(frozen=True)
class OntologyObject:
    id: str
    type: str
    attributes: Mapping

    def to_mapping(self):
        return {'id': self.id, 'type': self.type, 'attributes': dict(self.attributes)}


@dataclass(frozen=True)
class OntologyRelation:
    type: str
    from_id: str
    to_id: str
    evidence_ids: tuple[str, ...] = ()

    def to_mapping(self):
        return asdict(self)


@dataclass(frozen=True)
class OntologyBundle:
    schema_version: str
    source_fingerprint: str
    objects: tuple[OntologyObject, ...]
    relations: tuple[OntologyRelation, ...]
    action_types: tuple[ActionTypeSpec, ...]
    observations: tuple[Mapping, ...]
    counts: Mapping[str, int]

    def to_mapping(self):
        return dict(schema_version=self.schema_version, source_fingerprint=self.source_fingerprint,
                    objects=[o.to_mapping() for o in self.objects],
                    relations=[r.to_mapping() for r in self.relations],
                    action_types=[_action_mapping(a) for a in self.action_types],
                    observations=[dict(o) for o in self.observations], counts=dict(self.counts))


def _action_mapping(action):
    data = asdict(action)
    for key in ('inputs', 'outputs', 'evidence'):
        data[key] = list(data[key])
    return data


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def canonical_bundle_json(bundle: OntologyBundle) -> str:
    return canonical_json(bundle.to_mapping()) + '\n'


def safe_relative_path(value: str, *, prefix: str | None = None) -> str:
    if not isinstance(value, str) or not value or '\\' in value or any(ord(c) < 32 for c in value):
        raise OntologyProjectionError('invalid relative path')
    parts = value.split('/')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in {'', '.', '..'} for p in parts) or ':' in value:
        raise OntologyProjectionError('invalid relative path')
    if prefix and (len(parts) < 2 or parts[0] != prefix):
        raise OntologyProjectionError('relative path outside managed input')
    return value


def safe_slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[\w가-힣-]+(?:/[\w가-힣-]+)*', value):
        raise OntologyProjectionError('invalid knowledge identifier')
    return value


def _contained(path, root):
    if not path.resolve().is_relative_to(root.resolve()):
        raise OntologyProjectionError('input escapes project root')
    return path


def _post(path):
    try:
        return frontmatter.load(path)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError, RecursionError) as exc:
        raise OntologyProjectionError('knowledge metadata invalid') from exc


def _text(value):
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        raise OntologyProjectionError('knowledge metadata must be text')
    return value


def source_fingerprint(objects, relations, action_types, observations):
    return hashlib.sha256(canonical_json(dict(
        objects=[o.to_mapping() for o in objects], relations=[r.to_mapping() for r in relations],
        action_types=[_action_mapping(a) for a in action_types], observations=[dict(o) for o in observations],
    )).encode('utf-8')).hexdigest()


def _bundle(ontology, actions, objects, relations, observations=(), unknown=0):
    objects = tuple(sorted(objects, key=lambda o: (o.type, o.id)))
    relations = tuple(sorted(set(relations), key=lambda r: (r.type, r.from_id, r.to_id, r.evidence_ids)))
    action_types = tuple(sorted(actions.actions, key=lambda a: a.id))
    observations = tuple(sorted(observations, key=lambda o: o['id']))
    counts = MappingProxyType(dict(object_count=len(objects), relation_count=len(relations),
                                  action_type_count=len(action_types), observation_count=len(observations),
                                  unknown_episode_type_count=unknown))
    return OntologyBundle(ontology.schema_version,
                          source_fingerprint(objects, relations, action_types, observations),
                          objects, relations, action_types, observations, counts)


def build_private_bundle(project_root: Path, ontology: OntologyContract, actions: ActionCatalog) -> OntologyBundle:
    root = Path(project_root).resolve()
    wiki = root / 'wiki'
    objects = {}
    relations = []
    posts = {}

    def add(object_id, type_id, attributes):
        obj = OntologyObject(object_id, type_id, MappingProxyType(dict(attributes)))
        if object_id in objects and objects[object_id] != obj:
            raise OntologyProjectionError('conflicting duplicate ontology object')
        objects[object_id] = obj

    for category in claim_ledger._CATEGORIES:
        directory = _contained(wiki / category, root)
        for path in sorted(directory.rglob('*.md')):
            _contained(path, root)
            slug = safe_slug(path.relative_to(directory).with_suffix('').as_posix())
            if slug in posts:
                raise OntologyProjectionError('ambiguous knowledge page identifier')
            post = _post(path)
            scope = post.metadata.get('scope', 'shared')
            if scope not in {'private', 'shared'}:
                raise OntologyProjectionError('invalid page scope')
            attributes = dict(slug=slug, title=_text(post.metadata.get('title', slug)), scope=scope)
            for key in ('owner', 'updated'):
                if post.metadata.get(key) is not None:
                    attributes[key] = _text(post.metadata[key])
            add('page:' + slug, 'knowledge_page', attributes)
            posts[slug] = post

    ledger = root / 'claims.jsonl'
    try:
        records = claim_ledger.read_claims_jsonl(_contained(ledger, root)) if ledger.exists() else []
        if posts and not records:
            raise claim_ledger.ClaimLedgerError('missing claim inventory')
        # Containment is checked before the legacy validator reads the referenced page.
        for record in records:
            if claim_ledger.claim_slug(record) not in posts:
                raise claim_ledger.ClaimLedgerError('claim page missing')
            safe_relative_path(record.raw_path, prefix='raw')
            _contained(root / record.raw_path, root)
        claim_ledger.validate_claim_source_inventory(records, wiki_root=wiki)
    except claim_ledger.ClaimLedgerError as exc:
        raise OntologyProjectionError('ontology inventory invalid; recovery: ' + claim_ledger.CLAIM_REBUILD_COMMAND) from exc

    for record in records:
        source_id = 'source:' + record.raw_sha256
        add(source_id, 'source', dict(sha256=record.raw_sha256, relative_path=record.raw_path))
        attrs = record.to_mapping()
        attrs.pop('claim_id')
        add(record.claim_id, 'claim', attrs)
        relations.append(OntologyRelation('supports', source_id, record.claim_id, (record.claim_id,)))
        relations.append(OntologyRelation('compiled_into', record.claim_id,
                                           'page:' + claim_ledger.claim_slug(record), (record.claim_id,)))
    for slug, post in posts.items():
        for target in re.findall(r'\[\[([^\]|#]+)(?:[^\]]*)\]\]', post.content):
            if target in posts:
                relations.append(OntologyRelation('links_to', 'page:' + slug, 'page:' + target))
    procedures = _contained(root / 'procedures', root)
    for path in sorted(procedures.glob('*.md')):
        post = _post(_contained(path, root))
        slug = safe_slug(path.stem)
        attrs = dict(slug=slug, title=_text(post.metadata.get('title', slug)))
        if 'version' in post.metadata:
            attrs['version'] = str(post.metadata['version'])
        add('procedure:' + slug, 'procedure', attrs)
    # Optional episode history is projected without changing its fail-soft callers.
    import episode
    from lib.ontology_observations import observation_from_episode, action_for_task, artifact_id
    express = _contained(root / 'express', root)
    for path in sorted(express.rglob('*.md')):
        _contained(path, root)
        relative = safe_relative_path(path.relative_to(root).as_posix(), prefix='express')
        add(artifact_id(relative), 'artifact', dict(relative_path=relative, artifact_type=path.parent.name))
    episodes = _contained(root / 'episodes', root)
    for path in episodes.glob('*.jsonl'):
        _contained(path, root)
    try:
        records = episode.read_recent(episodes_dir=episodes, limit=sys.maxsize)
    except (OSError, UnicodeError):
        records = []  # Optional history must not block the canonical knowledge projection.
    observations = {}
    unknown = 0
    for record in records:
        if action_for_task(record.get('task_type')) is None:
            unknown += 1
            continue
        observation = observation_from_episode(record)
        if observation is None:
            continue
        if observation.action_type not in {a.id for a in actions.actions}:
            continue
        data = observation.to_mapping()
        for key in ('page_ids', 'procedure_ids', 'artifact_ids'):
            data[key] = tuple(ref for ref in data[key] if ref in objects)
        if data['id'] in observations and observations[data['id']] != data:
            raise OntologyProjectionError('conflicting observation identifier')
        observations[data['id']] = MappingProxyType(data)
        for artifact in data['artifact_ids']:
            for key, relation in (('page_ids', 'derived_from'), ('procedure_ids', 'guided_by')):
                for target in data[key]:
                    relations.append(OntologyRelation(relation, artifact, target, (data['id'],)))
    return _bundle(ontology, actions, objects.values(), relations, observations.values(), unknown)
