"""Wiki graph and ontology must agree on which page links actually exist."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_graph
from tests.test_ontology_projection import build


def test_export_and_projection_share_alias_ambiguity_and_self_link_rules(ontology_project, monkeypatch, tmp_path):
    wiki = ontology_project / 'wiki'
    projects = wiki / 'projects'
    for relative in ('team/topic', 'one/shared', 'two/shared', 'nested/alpha'):
        file = projects / (relative + '.md')
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('---\ntitle: Synthetic\n---\n')
    alpha = wiki / 'concepts/alpha.md'
    alpha.write_text(alpha.read_text() + '\n[[topic#part|label]] [[shared]] [[missing]] [[alpha]]\n')
    output = tmp_path / 'derived-graph.json'
    monkeypatch.setattr(export_graph, 'WIKI_DIR', wiki)
    monkeypatch.setattr(export_graph, 'OUTPUT', output)
    assert export_graph.main() == 0
    graph = json.loads(output.read_text())
    graph_links = {(x['source'], x['target']) for x in graph['links'] if x['kind'] == 'wikilink'}
    relations = {(r.from_id.removeprefix('page:'), r.to_id.removeprefix('page:'))
                 for r in build(ontology_project).relations if r.type == 'links_to'}
    assert graph_links == relations == {('alpha', 'team/topic')}
    ghosts = {x['id'] for x in graph['nodes'] if x['kind'] == 'ghost'}
    assert {'ghost:shared', 'ghost:missing'} <= ghosts


def test_exact_slug_takes_precedence_over_nested_basename(ontology_project, monkeypatch, tmp_path):
    wiki = ontology_project / 'wiki'
    (wiki / 'concepts/beta.md').write_text('---\ntitle: Beta\n---\n[[alpha]]\n')
    nested = wiki / 'projects/team/alpha.md'
    nested.parent.mkdir(parents=True)
    nested.write_text('---\ntitle: Nested alpha\n---\n')
    monkeypatch.setattr(export_graph, 'WIKI_DIR', wiki)
    monkeypatch.setattr(export_graph, 'OUTPUT', tmp_path / 'graph.json')
    export_graph.main()
    graph = json.loads((tmp_path / 'graph.json').read_text())
    links = {(e['source'], e['target']) for e in graph['links'] if e['kind'] == 'wikilink'}
    relations = {(r.from_id.removeprefix('page:'),r.to_id.removeprefix('page:'))
                 for r in build(ontology_project).relations if r.type == 'links_to'}
    assert links == relations == {('beta', 'alpha')}
