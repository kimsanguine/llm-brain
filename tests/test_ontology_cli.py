"""CLI output is private, atomic, and constrained to its managed directory."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.test_ontology_projection import snapshot

ROOT = Path(__file__).resolve().parents[1]


def run(root, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/ontology.py'), '--project-root', str(root), *args],
                          capture_output=True, text=True, cwd=root)


def test_validate_and_explain_do_not_write(ontology_project):
    before = snapshot(ontology_project)
    result = run(ontology_project, 'validate')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['counts']['object_count'] == 4
    result = run(ontology_project, 'explain', '--id', 'page:alpha')
    assert result.returncode == 0, result.stderr
    assert 'page:alpha' in result.stdout and 'claim:alpha-1' in result.stdout
    assert snapshot(ontology_project) == before


def test_export_is_deterministic_and_saved_bundle_explain_needs_no_project(ontology_project):
    for filename in ('first', 'second'):
        result = run(ontology_project, 'export', '--out', f'ontology/{filename}.json')
        assert result.returncode == 0, result.stderr
    first = ontology_project / 'ontology/first.json'
    assert first.read_bytes() == (ontology_project / 'ontology/second.json').read_bytes()
    result = run(ontology_project, 'explain', '--bundle', str(first), '--id', 'claim:alpha-1', '--json')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['focus']['id'] == 'claim:alpha-1'


@pytest.mark.parametrize('unsafe', ['raw/o.json', 'wiki/o.json', 'episodes/o.json', '../o.json',
                                  'ontology/../raw/o.json', 'ontology//o.json', '/tmp/o.json', 'ontology'])
def test_export_rejects_unmanaged_destinations_before_any_write(ontology_project, unsafe):
    before = snapshot(ontology_project)
    result = run(ontology_project, 'export', '--out', unsafe)
    assert result.returncode == 2
    assert snapshot(ontology_project) == before
    assert not (ontology_project / 'ontology').exists()


def test_export_rejects_symlink_targets(ontology_project, tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    (ontology_project / 'ontology').symlink_to(outside, target_is_directory=True)
    result = run(ontology_project, 'export')
    assert result.returncode == 2
    assert list(outside.iterdir()) == []


def test_atomic_failure_preserves_old_bundle_and_removes_stage(ontology_project, monkeypatch):
    import ontology
    from tests.test_ontology_projection import build
    directory = ontology_project / 'ontology'
    directory.mkdir()
    target = directory / 'private-ontology.json'
    target.write_text('OLD COMPLETE BUNDLE')
    def fail(*args):
        raise OSError('SECRET path')
    monkeypatch.setattr(ontology.os, 'replace', fail)
    with pytest.raises(ontology.OntologyProjectionError):
        ontology.export_bundle(build(ontology_project), ontology_project, 'ontology/private-ontology.json')
    assert target.read_text() == 'OLD COMPLETE BUNDLE'
    assert list(directory.iterdir()) == [target]


def test_nonempty_wiki_requires_ledger_and_safe_recovery(ontology_project):
    (ontology_project / 'claims.jsonl').write_text('{SECRET')
    result = run(ontology_project, 'validate')
    assert result.returncode == 2
    assert 'uv run python scripts/claims.py build' in result.stderr
    assert 'SECRET' not in result.stderr
    assert str(ontology_project) not in result.stderr


def test_empty_clone_and_missing_object_have_explicit_exits(tmp_path):
    assert run(tmp_path, 'validate').returncode == 0
    result = run(tmp_path, 'explain', '--id', 'page:SECRET')
    assert result.returncode == 2 and 'SECRET' not in result.stderr
