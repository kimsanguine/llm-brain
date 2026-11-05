"""Redacted, optional observations. These are not authorization or audit events."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

from lib.ontology_projection import canonical_json, safe_relative_path, safe_slug, OntologyProjectionError


@dataclass(frozen=True)
class ActionObservation:
    id: str
    action_type: str
    timestamp: str
    status: str
    page_ids: tuple[str, ...]
    procedure_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]

    def to_mapping(self):
        return asdict(self)


def action_for_task(task):
    if task == 'ai_answer':
        return 'query'
    if isinstance(task, str) and task.startswith('express_'):
        return 'express'
    if task in ('ingest', 'ingest_url', 'ingest_file', 'ingest_note'):
        return 'ingest'
    return 'curate' if task == 'curate' else None


def _reference(value, kind):
    if not isinstance(value, str):
        return None
    try:
        if value.startswith(kind + ':'):
            slug = value[len(kind) + 1:]
        else:
            value = safe_relative_path(value)
            parts = value.removesuffix('.md').split('/')
            if kind == 'page':
                if parts[0] == 'wiki':
                    parts.pop(0)
                if len(parts) > 1 and parts[0] in {'concepts', 'tools', 'people', 'projects', 'business', 'lecture', 'insights'}:
                    parts.pop(0)
            elif parts[0] == 'procedures':
                parts.pop(0)
            slug = '/'.join(parts)
        return kind + ':' + safe_slug(slug)
    except OntologyProjectionError:
        return None


def artifact_id(path):
    safe_relative_path(path, prefix='express')
    return 'artifact:' + hashlib.sha256(path.encode('utf-8')).hexdigest()[:16]


def artifact_paths(record):
    outputs = record.get('outputs')
    if not isinstance(outputs, dict):
        return ()
    path = outputs.get('draft_path')
    try:
        safe_relative_path(path, prefix='express')
    except OntologyProjectionError:
        return ()
    return (path,)


def observation_from_episode(record) -> ActionObservation | None:
    action = action_for_task(record.get('task_type'))
    if action is None:
        return None
    timestamp = record.get('timestamp')
    try:
        datetime.fromisoformat(timestamp)
        digest = hashlib.sha256(canonical_json(record).encode('utf-8')).hexdigest()[:16]
    except (ValueError, TypeError, RecursionError):
        return None
    status = record.get('status')
    if not isinstance(status, str) or status not in {'ok', 'draft_ready', 'pending_wiki_compilation', 'success', 'error', 'timeout',
                      'abstained', 'unavailable', 'answered', 'failed', 'unknown'}:
        status = 'unknown'

    def references(key, kind):
        values = record.get(key)
        if not isinstance(values, list):
            return ()
        return tuple(sorted({ref for value in values if (ref := _reference(value, kind)) is not None}))

    return ActionObservation('observation:' + digest, action, timestamp, status,
                             references('read_pages', 'page'), references('procedures_used', 'procedure'),
                             tuple(sorted(artifact_id(path) for path in artifact_paths(record))))
