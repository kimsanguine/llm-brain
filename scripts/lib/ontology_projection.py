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
from lib.wiki_frontmatter import load_wiki_post
from lib.ontology_contract import OntologyContract, ActionCatalog, ActionTypeSpec


CLAIM_RECOVERY_HELP = claim_ledger.CLAIM_RECOVERY_HELP


class OntologyProjectionError(ValueError):
    """Safe aggregate diagnostic, without personal statements or paths."""


@dataclass(frozen=True)
class OntologyObject:
    id: str
    type: str
    attributes: Mapping

    def to_mapping(self):
        attributes = dict(self.attributes)
        if 'source_binding' in attributes:
            attributes['source_binding'] = dict(attributes['source_binding'])
        if 'relative_paths' in attributes:
            attributes['relative_paths'] = list(attributes['relative_paths'])
        return {'id': self.id, 'type': self.type, 'attributes': attributes}


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


def _post(path, *, allow_legacy_title=False):
    try:
        return load_wiki_post(path, allow_legacy_title=allow_legacy_title)
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
            post = _post(path, allow_legacy_title=category == 'papers')
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
        raise OntologyProjectionError('ontology inventory invalid; recovery: ' + CLAIM_RECOVERY_HELP) from exc

    source_paths = {}
    for record in records:
        source_paths.setdefault(record.raw_sha256, set()).add(record.raw_path)
    for sha, paths in sorted(source_paths.items()):
        paths = tuple(sorted(paths))
        attrs = dict(sha256=sha, relative_path=paths[0])
        if len(paths) > 1:
            attrs['relative_paths'] = paths
        add('source:' + sha, 'source', attrs)
    for record in records:
        source_id = 'source:' + record.raw_sha256
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
    bundle = _bundle(ontology, actions, objects.values(), relations, observations.values(), unknown)
    return validate_bundle_mapping(bundle.to_mapping(), ontology)


class OntologyObjectNotFound(OntologyProjectionError):
    pass


def _strict_keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        raise OntologyProjectionError('bundle has missing or unknown fields')


def _string(value):
    if not isinstance(value, str) or not value.strip():
        raise OntologyProjectionError('bundle field must be nonempty text')
    return value


def _sequence(value):
    if not isinstance(value, (list, tuple)):
        raise OntologyProjectionError('bundle field must be a list')
    return value


def _unique_ids(items):
    if len({item.id for item in items}) != len(items):
        raise OntologyProjectionError('duplicate bundle identifier')


def validate_bundle_mapping(data, ontology: OntologyContract) -> OntologyBundle:
    """Validate loaded and freshly projected bundles through a single boundary."""
    from lib.ontology_contract import action_from_mapping, OntologyContractError
    _strict_keys(data, ('schema_version', 'source_fingerprint', 'objects', 'relations', 'action_types', 'observations', 'counts'))
    if data['schema_version'] != ontology.schema_version:
        raise OntologyProjectionError('unsupported bundle schema version')
    specs = {spec.id: spec for spec in ontology.object_types}
    allowed = {
        'source': {'sha256', 'relative_path', 'relative_paths'},
        'claim': {'statement', 'kind', 'status', 'trust', 'valid_from', 'valid_until', 'raw_path', 'raw_sha256', 'locator', 'source_binding'},
        'knowledge_page': {'slug', 'title', 'scope', 'owner', 'updated'},
        'procedure': {'slug', 'title', 'version'},
        'artifact': {'relative_path', 'artifact_type'},
    }
    objects = []
    for raw in _sequence(data['objects']):
        _strict_keys(raw, ('id', 'type', 'attributes'))
        object_id, kind, attrs = raw['id'], raw['type'], raw['attributes']
        _string(object_id)
        if not isinstance(kind, str) or kind not in specs or kind not in allowed:
            raise OntologyProjectionError('unknown object type')
        _strict_keys(attrs, specs[kind].required_attributes, allowed[kind] - set(specs[kind].required_attributes))
        for key, value in attrs.items():
            if (kind, key) not in {('claim', 'source_binding'), ('source', 'relative_paths')}:
                _string(value)
        if kind == 'source':
            if re.fullmatch('[0-9a-f]{64}', attrs['sha256']) is None or object_id != 'source:' + attrs['sha256']:
                raise OntologyProjectionError('invalid source identity')
            safe_relative_path(attrs['relative_path'], prefix='raw')
            if 'relative_paths' in attrs:
                paths = tuple(safe_relative_path(path, prefix='raw') for path in _sequence(attrs['relative_paths']))
                if len(paths) < 2 or paths != tuple(sorted(set(paths))) or attrs['relative_path'] != paths[0]:
                    raise OntologyProjectionError('invalid source path aliases')
                attrs = dict(attrs, relative_paths=paths)
        elif kind == 'claim':
            try:
                record = claim_ledger.ClaimRecord(claim_id=object_id, locator=attrs.get('locator'), **{k: v for k, v in attrs.items() if k != 'locator'})
                if record.source_binding is not None:
                    attrs = dict(attrs, source_binding=MappingProxyType(asdict(record.source_binding)))
            except (claim_ledger.ClaimLedgerError, TypeError) as exc:
                raise OntologyProjectionError('invalid claim object') from exc
        elif kind in {'knowledge_page', 'procedure'}:
            slug = safe_slug(attrs['slug'])
            prefix = 'page' if kind == 'knowledge_page' else 'procedure'
            if object_id != prefix + ':' + slug:
                raise OntologyProjectionError('invalid object identity')
            if kind == 'knowledge_page' and attrs['scope'] not in {'private', 'shared'}:
                raise OntologyProjectionError('invalid page scope')
        else:
            from lib.ontology_observations import artifact_id
            if object_id != artifact_id(attrs['relative_path']):
                raise OntologyProjectionError('invalid artifact identity')
        objects.append(OntologyObject(object_id, kind, MappingProxyType(dict(attrs))))
    _unique_ids(objects)
    by_id = {obj.id: obj for obj in objects}
    actions = []
    try:
        for raw in _sequence(data['action_types']):
            actions.append(action_from_mapping(raw, ontology))
    except OntologyContractError as exc:
        raise OntologyProjectionError('invalid bundle action catalog') from exc
    _unique_ids(actions)
    observations = []
    action_ids = {a.id for a in actions}
    for raw in _sequence(data['observations']):
        _strict_keys(raw, ('id', 'action_type', 'timestamp', 'status', 'page_ids', 'procedure_ids', 'artifact_ids'))
        if not isinstance(raw['id'], str) or re.fullmatch(r'observation:[0-9a-f]{16}', raw['id']) is None:
            raise OntologyProjectionError('invalid observation identity')
        if raw['action_type'] not in action_ids:
            raise OntologyProjectionError('unknown observation action')
        from datetime import datetime
        try:
            datetime.fromisoformat(raw['timestamp'])
        except (ValueError, TypeError) as exc:
            raise OntologyProjectionError('invalid observation timestamp') from exc
        if raw['status'] not in {'ok', 'draft_ready', 'pending_wiki_compilation', 'success', 'error', 'timeout',
                                 'abstained', 'unavailable', 'answered', 'failed', 'unknown'}:
            raise OntologyProjectionError('invalid observation status')
        value = dict(raw)
        for key, kind in (('page_ids', 'knowledge_page'), ('procedure_ids', 'procedure'), ('artifact_ids', 'artifact')):
            refs = tuple(_sequence(raw[key]))
            if any(not isinstance(ref, str) or ref not in by_id or by_id[ref].type != kind for ref in refs):
                raise OntologyProjectionError('invalid observation reference')
            if refs != tuple(sorted(set(refs))):
                raise OntologyProjectionError('observation references must be sorted and unique')
            value[key] = refs
        observations.append(MappingProxyType(value))
    observation_ids = {o['id'] for o in observations}
    if len(observation_ids) != len(observations):
        raise OntologyProjectionError('duplicate observation identifier')
    relations = []
    relation_specs = {spec.id: spec for spec in ontology.relation_types}
    for raw in _sequence(data['relations']):
        _strict_keys(raw, ('type', 'from_id', 'to_id', 'evidence_ids'))
        if not all(isinstance(raw[k], str) for k in ('type', 'from_id', 'to_id')):
            raise OntologyProjectionError('invalid relation identity')
        spec = relation_specs.get(raw['type'])
        left, right = by_id.get(raw['from_id']), by_id.get(raw['to_id'])
        if not spec or not left or not right or left.type != spec.from_type or right.type != spec.to_type:
            raise OntologyProjectionError('invalid relation endpoints')
        if spec.id == 'supports' and (
            left.attributes['sha256'] != right.attributes['raw_sha256']
            or right.attributes['raw_path'] not in left.attributes.get('relative_paths', (left.attributes['relative_path'],))
        ):
            raise OntologyProjectionError('source relation disagrees with claim provenance')
        if spec.id == 'compiled_into' and right.id != left.id.rsplit('-', 1)[0].replace('claim:', 'page:', 1):
            raise OntologyProjectionError('page relation disagrees with claim identity')
        evidence = tuple(_sequence(raw['evidence_ids']))
        if any(not isinstance(ref, str) or (ref not in observation_ids and (ref not in by_id or by_id[ref].type != 'claim')) for ref in evidence):
            raise OntologyProjectionError('invalid relation evidence')
        relations.append(OntologyRelation(raw['type'], raw['from_id'], raw['to_id'], evidence))
    if len(set(relations)) != len(relations):
        raise OntologyProjectionError('duplicate relation')
    count_keys = ('object_count', 'relation_count', 'action_type_count', 'observation_count', 'unknown_episode_type_count')
    _strict_keys(data['counts'], count_keys)
    counts = data['counts']
    if any(type(value) is not int or value < 0 for value in counts.values()):
        raise OntologyProjectionError('invalid bundle counts')
    if [counts[k] for k in count_keys[:4]] != [len(objects), len(relations), len(actions), len(observations)]:
        raise OntologyProjectionError('inconsistent bundle counts')
    bundle = _bundle(ontology, ActionCatalog('llm-brain-actions/0.1', tuple(actions)), objects, relations, observations,
                     counts['unknown_episode_type_count'])
    if data['source_fingerprint'] != bundle.source_fingerprint:
        raise OntologyProjectionError('bundle fingerprint mismatch')
    return bundle


def _json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise OntologyProjectionError('duplicate bundle JSON key')
        result[key] = value
    return result


def read_bundle(path: Path, ontology: OntologyContract | None = None) -> OntologyBundle:
    from lib.ontology_contract import load_ontology_contract
    if ontology is None:
        ontology = load_ontology_contract(Path(__file__).resolve().parents[2] / 'schema/ontology.yaml')
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_json_pairs)
        return validate_bundle_mapping(data, ontology)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise OntologyProjectionError('saved ontology bundle invalid') from exc


@dataclass(frozen=True)
class ExplanationStep:
    relation: str
    object_id: str
    object_type: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class Explanation:
    focus: OntologyObject
    incoming: tuple[ExplanationStep, ...]
    outgoing: tuple[ExplanationStep, ...]
    policy_notes: tuple[str, ...]
    objects: tuple[OntologyObject, ...]
    relations: tuple[OntologyRelation, ...]
    claim_counts: Mapping[str, int]

    def to_mapping(self):
        return dict(focus=self.focus.to_mapping(), incoming=[asdict(s) for s in self.incoming],
                    outgoing=[asdict(s) for s in self.outgoing], policy_notes=list(self.policy_notes),
                    objects=[o.to_mapping() for o in self.objects], relations=[r.to_mapping() for r in self.relations],
                    claim_counts=dict(self.claim_counts))


def explain_object(bundle: OntologyBundle, object_id: str) -> Explanation:
    objects = {obj.id: obj for obj in bundle.objects}
    if object_id not in objects:
        raise OntologyObjectNotFound('unknown object id')
    focus = objects[object_id]
    def steps(incoming):
        found = []
        for relation in bundle.relations:
            if (relation.to_id if incoming else relation.from_id) == object_id:
                other = objects[relation.from_id if incoming else relation.to_id]
                found.append(ExplanationStep(relation.type, other.id, other.type, relation.evidence_ids))
        return tuple(sorted(found, key=lambda s: (s.relation, s.object_id, s.evidence_ids)))
    incoming, outgoing = steps(True), steps(False)
    related = {object_id} | {step.object_id for step in incoming + outgoing}
    # A page's direct claims lead one step farther upstream to their sources.
    for relation in bundle.relations:
        if (relation.type == 'supports' and relation.to_id in related) or (relation.type == 'guided_by' and relation.from_id in related):
            related.update((relation.from_id, relation.to_id))
    notes = []
    if focus.type == 'claim':
        if focus.attributes['status'] != 'active':
            notes.append('claim is ' + focus.attributes['status'])
        if focus.attributes['trust'] == 'untrusted':
            notes.append('claim is untrusted')
    if focus.type == 'knowledge_page' and focus.attributes['scope'] == 'private':
        notes.append('page scope is private')
    claim_ids = {s.object_id for s in incoming if s.relation == 'compiled_into'}
    if focus.type == 'claim':
        claim_ids.add(focus.id)
    claims = [objects[id] for id in sorted(claim_ids)]
    counts = {state: sum(o.attributes['status'] == state for o in claims) for state in ('active', 'stale', 'superseded')}
    counts.update({trust: sum(o.attributes['trust'] == trust for o in claims) for trust in ('trusted', 'untrusted')})
    return Explanation(focus, incoming, outgoing, tuple(sorted(notes)),
                       tuple(o for o in bundle.objects if o.id in related),
                       tuple(r for r in bundle.relations if r.from_id in related and r.to_id in related), MappingProxyType(counts))
