---
description: Validate, export, or explain the private Personal Knowledge Ontology
argument-hint: validate | export | explain --id <object-id>
---

# Personal Knowledge Ontology

Read `CLAUDE.md` first. Work from the cloned llm-brain repository and use
`scripts/ontology.py`. This command describes knowledge and existing commands;
it does not execute actions from the catalog.

| User intent | Script operation | Writes |
|---|---|---|
| ontology 점검해줘 | `validate` | none |
| ontology bundle 만들어줘 | `validate`, then `export` | `ontology/` only |
| claim:alpha-1 근거를 설명해줘 | `explain --id claim:alpha-1` | none |

```bash
uv run python scripts/ontology.py validate
uv run python scripts/ontology.py export
uv run python scripts/ontology.py explain --id page:alpha
uv run python scripts/ontology.py explain --bundle examples/ontology-bundle-example.json --id claim:alpha-1 --json
```

Inspect the strict contracts and validation counts before export. A nonempty wiki
requires a valid persisted claim ledger. On invalid inventory, report the safe
recovery command `uv run python scripts/claims.py build`; rebuilding claims is a
separate write and must stay within the user's request.

Report the exact written path and `source_fingerprint`. Generated bundles contain
private claim statements. Export is private and does not authorize sharing.
Never run `okf --share`, publish a bundle, or change any external system as a
side effect. The existing OKF share approval gate remains separate.

Observations are optional, redacted projections of fail-soft episode history.
Do not call them mandatory audit events or use them for permission/approval.
No raw/wiki bodies, episode goals, input/output prose, or notes enter the bundle.
Validate and explain never export or record episodes.
