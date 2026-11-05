"""Legacy paper title compatibility must never repair source metadata."""
import hashlib
from datetime import date
from pathlib import Path
import sys

import frontmatter
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def paper(title='Synthetic: Paper', source='[raw/notes/paper.md]'):
    return f'---\ntitle: {title}\nsources: {source}\nupdated: 2026-11-05\n---\n\nAlpha source fact.\n'


def test_unquoted_colon_title_is_read_without_rewriting_file(tmp_path):
    from lib.wiki_frontmatter import load_wiki_post
    path = tmp_path / 'paper.md'
    path.write_text(paper())
    before = path.read_bytes()
    post = load_wiki_post(path, allow_legacy_title=True)
    assert post['title'] == 'Synthetic: Paper'
    assert post['sources'] == ['raw/notes/paper.md']
    assert post.content == 'Alpha source fact.'
    assert path.read_bytes() == before


def test_normal_documents_keep_existing_frontmatter_behavior():
    from lib.wiki_frontmatter import loads_wiki_post
    text = paper('"Already quoted: Title"')
    post = loads_wiki_post(text, allow_legacy_title=True)
    assert post.metadata == {'title': 'Already quoted: Title', 'sources': ['raw/notes/paper.md'], 'updated': date(2026, 11, 5)}
    assert post.content == 'Alpha source fact.'


@pytest.mark.parametrize('text,allowed', [
    (paper(), False),
    (paper(source='[raw/notes/paper.md'), True),
    (paper('"Unclosed: Title'), True),
    (paper('!!python/object:unsafe'), True),
    (paper().replace('sources:', 'title: Another\nsources:'), True),
])
def test_bad_metadata_does_not_gain_authority_from_title_fallback(text, allowed):
    from lib.wiki_frontmatter import loads_wiki_post
    with pytest.raises(yaml.YAMLError):
        loads_wiki_post(text, allow_legacy_title=allowed)


def test_colon_title_and_body_lines_are_not_confused():
    from lib.wiki_frontmatter import loads_wiki_post
    text = paper() + '\ntitle: Body: Literal\n'
    post = loads_wiki_post(text, allow_legacy_title=True)
    assert post.content == 'Alpha source fact.\n\ntitle: Body: Literal'


def test_paper_lookup_search_and_binding_share_same_read_only_parser(tmp_path):
    from lib import claim_ledger, claim_source_map
    from lib.ontology_contract import load_ontology_contract, load_action_catalog
    from lib.ontology_projection import build_private_bundle
    from wiki_app.api import create_app
    from fastapi.testclient import TestClient
    root = tmp_path
    (root / 'wiki/papers').mkdir(parents=True)
    (root / 'raw/notes').mkdir(parents=True)
    page = root / 'wiki/papers/sample.md'
    page.write_text(paper())
    (root / 'raw/notes/paper.md').write_text('Alpha source fact.\n')
    (root / 'index.md').write_text('## papers/\n- [[sample]] — Synthetic paper\n')
    proposed = claim_source_map.propose_source_map(['sample'], wiki_root=root / 'wiki')
    assert len(proposed['mappings']) == 1
    assert proposed['mappings'][0]['source_binding']['page_sha256'] == hashlib.sha256(page.read_bytes()).hexdigest()
    records = claim_ledger.build_claim_ledger(['sample'], wiki_root=root / 'wiki',
        source_map={m['claim_id']: m for m in proposed['mappings']})
    claim_ledger.write_claims_jsonl(root / 'claims.jsonl', records, project_root=root)
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    claim_ledger.validate_claim_source_inventory(records, wiki_root=root / 'wiki')
    assert claim_ledger.claim_exclusion_reason(records[0], project_root=root) is None
    ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
    bundle = build_private_bundle(root, ontology, load_action_catalog(ROOT / 'schema/actions.yaml', ontology))
    assert next(o for o in bundle.objects if o.id == 'page:sample').attributes['title'] == 'Synthetic: Paper'
    client = TestClient(create_app(wiki_root=root / 'wiki'))
    assert client.get('/api/page/sample').status_code == 200
    assert client.get('/api/search', params={'q': 'Synthetic: Paper'}).json()['total'] == 1
    assert client.get('/api/ontology/page/sample').status_code == 200
    assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
