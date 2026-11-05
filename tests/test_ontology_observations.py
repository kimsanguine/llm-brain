"""Only normalized references, never episode prose, cross the observation boundary."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.ontology_observations import observation_from_episode
from tests.test_ontology_projection import build


def record(**changes):
    data = dict(timestamp='2026-01-01T00:00:00+00:00', task_type='express_blog',
                user_goal='SECRET GOAL', inputs={'secret': 'SECRET INPUT'},
                outputs={'draft_path': 'express/blog/a.md', 'secret': 'SECRET OUTPUT'},
                notes='SECRET NOTE', read_pages=['wiki/concepts/alpha.md'],
                procedures_used=['review'], status='draft_ready')
    data.update(changes)
    return data


def test_redacts_prose_and_hashes_artifact_path():
    observation = observation_from_episode(record())
    data = observation.to_mapping()
    encoded = json.dumps(data)
    assert 'SECRET' not in encoded
    assert 'express/blog/a.md' not in encoded
    assert data['page_ids'] == ('page:alpha',)
    assert data['procedure_ids'] == ('procedure:review',)
    assert data['artifact_ids'] == ('artifact:' + hashlib.sha256(b'express/blog/a.md').hexdigest()[:16],)
    assert observation_from_episode(dict(reversed(list(record().items())))) == observation


@pytest.mark.parametrize('task,action', [
    ('ai_answer', 'query'), ('express_blog', 'express'), ('express_report', 'express'),
    ('ingest', 'ingest'), ('ingest_url', 'ingest'), ('ingest_file', 'ingest'),
    ('ingest_note', 'ingest'), ('curate', 'curate'),
])
def test_maps_existing_task_types(task, action):
    assert observation_from_episode(record(task_type=task)).action_type == action


@pytest.mark.parametrize('path', ['/Users/private/secret.md', 'express/../raw/a.md',
                                  'express//a.md', 'raw/a.md', 'express\\a.md'])
def test_does_not_hash_unsafe_artifact_paths(path):
    assert observation_from_episode(record(outputs={'draft_path': path})).artifact_ids == ()


def test_unknown_or_malformed_records_are_excluded():
    assert observation_from_episode(record(task_type='unknown')) is None
    assert observation_from_episode(record(timestamp='SECRET')) is None
    assert observation_from_episode(record(status='SECRET STATUS')).status == 'unknown'
    obs = observation_from_episode(record(read_pages=['../raw/secret.md', '/Users/private'], procedures_used=['../secret']))
    assert obs.page_ids == obs.procedure_ids == ()


def test_wires_observations_and_artifact_relations_without_mutation(ontology_project):
    (ontology_project / 'express/blog').mkdir(parents=True)
    (ontology_project / 'express/blog/a.md').write_text('SECRET ARTIFACT BODY')
    episodes = ontology_project / 'episodes'
    episodes.mkdir()
    shard = episodes / '2026-01.jsonl'
    shard.write_text(json.dumps(record()) + '\n{broken\n' + json.dumps(record(task_type='reweave')) + '\n')
    bundle = build(ontology_project)
    assert bundle.counts['observation_count'] == 1
    assert bundle.counts['unknown_episode_type_count'] == 1
    assert {(r.type, r.to_id) for r in bundle.relations if r.type in {'derived_from', 'guided_by'}} == {
        ('derived_from', 'page:alpha'), ('guided_by', 'procedure:review')}
    assert 'SECRET' not in json.dumps(bundle.to_mapping())
    assert '{broken' in shard.read_text()


def test_malformed_optional_status_cannot_block_knowledge_projection(ontology_project):
    data = record(status={'SECRET': 'not a status'})
    assert observation_from_episode(data).status == 'unknown'
    path = ontology_project / 'episodes'
    path.mkdir()
    (path / '2026-01.jsonl').write_text(json.dumps(data)+'\n')
    assert build(ontology_project).counts['observation_count'] == 1
