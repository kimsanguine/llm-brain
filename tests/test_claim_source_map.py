"""Source-map proposals expose uncertainty and never silently rewrite a ledger."""
from datetime import date
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import claim_ledger
from tests.test_claim_source_binding import mixed_project


def proposal(root):
    from lib import claim_source_map
    return claim_source_map.propose_source_map(['mixed'], wiki_root=root / 'wiki')


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def cli(root, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/claims.py'), *args],
                          cwd=root, text=True, capture_output=True)


def test_proposal_is_deterministic_read_only_and_omits_unmatched_claim(tmp_path):
    root = mixed_project(tmp_path)
    before = snapshot(root)
    result = proposal(root)
    assert result['schema_version'] == 'llm-brain-claim-source-map/0.1'
    assert [m['claim_id'] for m in result['mappings']] == ['claim:mixed-1', 'claim:mixed-2']
    assert result['unresolved'] == [{'claim_id': 'claim:mixed-3', 'reason': 'no_exact_match'}]
    assert result == proposal(root)
    assert snapshot(root) == before


def test_ambiguous_sources_cannot_select_first_or_launder_trust(tmp_path):
    root = mixed_project(tmp_path)
    (root / 'raw/captures/beta.md').write_text('Alpha fact.\nBeta claim.\n')
    result = proposal(root)
    assert [m['claim_id'] for m in result['mappings']] == ['claim:mixed-2']
    assert result['unresolved'][0] == {'claim_id': 'claim:mixed-1', 'reason': 'ambiguous_sources'}


def test_unsafe_external_and_missing_sources_are_not_evidence(tmp_path):
    root = mixed_project(tmp_path)
    page = root / 'wiki/concepts/mixed.md'
    page.write_text(page.read_text().replace('raw/notes/alpha.md', '../../outside.md')
                    .replace('raw/captures/beta.md', 'https://example.invalid/source'))
    result = proposal(root)
    assert result['mappings'] == []
    assert {v['reason'] for v in result['unresolved']} == {'no_safe_sources'}


@pytest.mark.parametrize('damage', ['version', 'duplicate', 'overlap', 'unknown', 'bad_binding', 'duplicate_json_key'])
def test_source_map_loader_is_strict_before_any_build(tmp_path, damage):
    from lib import claim_source_map
    root = mixed_project(tmp_path)
    data = proposal(root)
    if damage == 'version':
        data['schema_version'] = 'future'
    elif damage == 'duplicate':
        data['mappings'].append(copy.deepcopy(data['mappings'][0]))
    elif damage == 'overlap':
        data['unresolved'].append({'claim_id': 'claim:mixed-1', 'reason': 'no_exact_match'})
    elif damage == 'unknown':
        data['approved'] = True
    elif damage == 'bad_binding':
        data['mappings'][0]['source_binding']['quote'] = 'Forged.'
    text = json.dumps(data)
    if damage == 'duplicate_json_key':
        text = text.replace('"quote": "Alpha fact."', '"quote": "Forged.", "quote": "Alpha fact."')
    path = root / 'source-map.json'
    path.write_text(text)
    with pytest.raises(claim_ledger.ClaimLedgerError):
        claim_source_map.read_source_map(path)


def test_cli_propose_build_context_and_failed_build_preserve_ledger(tmp_path):
    root = mixed_project(tmp_path)
    before = snapshot(root)
    proposed = cli(root, 'propose', '--slug', 'mixed')
    assert proposed.returncode == 0, proposed.stderr
    assert snapshot(root) == before
    path = root / 'source-map.json'
    path.write_text(proposed.stdout)
    built = cli(root, 'build', '--slug', 'mixed', '--source-map', str(path))
    assert built.returncode == 0, built.stderr
    assert '2 records' in built.stdout and '1 unresolved' in built.stdout
    records = claim_ledger.read_claims_jsonl(root / 'claims.jsonl')
    assert len(records) == 2
    context = cli(root, 'context', '--slug', 'mixed')
    assert context.returncode == 0, context.stderr
    trusted = json.loads(next(line.split('=', 1)[1] for line in context.stdout.splitlines()
                              if line.startswith('TRUSTED_DATA_JSON=')))
    assert [r['claim_id'] for r in trusted] == ['claim:mixed-1']
    original_ledger = (root / 'claims.jsonl').read_bytes()
    (root / 'raw/notes/alpha.md').write_text('Changed.\n')
    failed = cli(root, 'build', '--slug', 'mixed', '--source-map', str(path))
    assert failed.returncode == 2
    assert (root / 'claims.jsonl').read_bytes() == original_ledger


def test_zero_mapped_build_cannot_erase_existing_ledger(tmp_path):
    root = mixed_project(tmp_path)
    data = proposal(root)
    data['mappings'] = []
    data['unresolved'] = [{'claim_id': f'claim:mixed-{n}', 'reason': 'no_exact_match'} for n in (1, 2, 3)]
    (root / 'map.json').write_text(json.dumps(data))
    (root / 'claims.jsonl').write_text('preserve existing ledger bytes\n')
    result = cli(root, 'build', '--slug', 'mixed', '--source-map', 'map.json')
    assert result.returncode == 2
    assert (root / 'claims.jsonl').read_text() == 'preserve existing ledger bytes\n'


def test_removed_selected_page_cannot_silently_truncate_existing_ledger(tmp_path):
    from lib import claim_source_map
    root = mixed_project(tmp_path)
    page = root / 'wiki/concepts/mixed.md'
    other = root / 'wiki/concepts/other.md'
    other.write_bytes(page.read_bytes())
    data = claim_source_map.propose_source_map(['mixed', 'other'], wiki_root=root / 'wiki')
    (root / 'map.json').write_text(json.dumps(data))
    args = ('build', '--slug', 'mixed', '--slug', 'other', '--source-map', 'map.json')
    assert cli(root, *args).returncode == 0
    before = (root / 'claims.jsonl').read_bytes()
    other.unlink()
    result = cli(root, *args)
    assert result.returncode == 2
    assert (root / 'claims.jsonl').read_bytes() == before
