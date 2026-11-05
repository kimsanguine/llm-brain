#!/usr/bin/env python3
"""Validate, export, and explain a private local knowledge projection. No LLM calls."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
from lib.ontology_contract import load_ontology_contract, load_action_catalog, OntologyContractError
from lib.ontology_projection import (build_private_bundle, canonical_bundle_json, canonical_json,
                                     explain_object, read_bundle, safe_relative_path, OntologyProjectionError)

ROOT = Path(__file__).resolve().parents[1]


def export_bundle(bundle, project_root: Path, output: str) -> Path:
    safe_relative_path(output, prefix='ontology')
    root = Path(project_root).resolve()
    destination = root / output
    if destination.suffix != '.json':
        raise OntologyProjectionError('export destination must be a JSON file below ontology/')
    current = root
    for part in Path(output).parts:
        current = current / part
        if current.is_symlink():
            raise OntologyProjectionError('export destination contains a symlink')
    if not destination.resolve().is_relative_to(root / 'ontology'):
        raise OntologyProjectionError('unsafe export destination')
    stage = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent,
                                         prefix='.ontology-', suffix='.tmp', delete=False) as stream:
            stage = Path(stream.name)
            stream.write(canonical_bundle_json(bundle))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(stage, destination)
    except OSError as exc:
        raise OntologyProjectionError('ontology export failed; previous bundle preserved') from exc
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
    return destination


def render_explanation(explanation):
    lines = [f'# {explanation.focus.id}', '']
    attrs = explanation.focus.attributes
    if attrs.get('title'):
        lines.append(attrs['title'])
    for step in explanation.incoming:
        lines.append(f'- {step.object_id} → {step.relation} → {explanation.focus.id}')
    for step in explanation.outgoing:
        lines.append(f'- {explanation.focus.id} → {step.relation} → {step.object_id}')
    for obj in explanation.objects:
        if obj.type == 'source':
            lines.append(f"- Source: {obj.attributes['relative_path']} ({obj.attributes['sha256'][:12]})")
    lines.extend('- ' + note for note in explanation.policy_notes)
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validate')
    export = commands.add_parser('export')
    export.add_argument('--out', default='ontology/private-ontology.json')
    explain = commands.add_parser('explain')
    explain.add_argument('--id', required=True)
    explain.add_argument('--bundle', type=Path)
    explain.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        ontology = load_ontology_contract(ROOT / 'schema/ontology.yaml')
        if args.command == 'explain' and args.bundle:
            bundle = read_bundle(args.bundle, ontology)
        else:
            # Canonical contracts ship with the compiler; project data stays independently located.
            actions = load_action_catalog(ROOT / 'schema/actions.yaml', ontology)
            bundle = build_private_bundle(args.project_root, ontology, actions)
        if args.command == 'explain':
            explanation = explain_object(bundle, args.id)
            print(canonical_json(explanation.to_mapping()) if args.json else render_explanation(explanation),
                  end='\n' if args.json else '')
        else:
            result = dict(counts=dict(bundle.counts), source_fingerprint=bundle.source_fingerprint)
            if args.command == 'export':
                result['written_path'] = str(export_bundle(bundle, args.project_root, args.out))
            print(canonical_json(result))
        return 0
    except (OntologyContractError, OntologyProjectionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        print('ontology inventory invalid; recovery: uv run python scripts/claims.py build', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
