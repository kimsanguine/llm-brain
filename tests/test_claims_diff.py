from dataclasses import replace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lib.claim_ledger import read_claims_jsonl
from scripts.claims_diff import compare


def test_moved_sentence_and_reused_id_are_distinguished(ontology_project):
    original = read_claims_jsonl(ontology_project / 'claims.jsonl')[0]
    moved = replace(original, claim_id='claim:alpha-2')
    other = replace(original, statement='A different statement.')
    result = compare([original], [moved, other])
    assert result['changes'][0]['match'] == 'moved_id'
    assert result['changes'][0]['new_id'] == moved.claim_id
    assert result['added_ids'] == [other.claim_id]
    assert result['removed_ids'] == []


def test_trust_change_is_visible_without_printing_statement(ontology_project):
    original = read_claims_jsonl(ontology_project / 'claims.jsonl')[0]
    result = compare([original], [replace(original, trust='untrusted')])
    assert result['changes'][0]['changed_fields'] == ['trust']
    assert result['changes'][0]['old_trust'] == 'trusted'
    assert result['changes'][0]['new_trust'] == 'untrusted'
    assert original.statement not in str(result)
