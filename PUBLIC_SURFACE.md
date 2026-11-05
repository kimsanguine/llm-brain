# Public Surface Policy

This repository contains the portable compiler, commands, schemas, examples,
and public assets required for a fresh installation.

- Any `docs` or `.archive` directory at any depth is local/private and must not
  be committed.
- Personal `raw/`, `wiki/`, episode, and generated express content are local
  data and remain excluded from Git.
- Product planning, progress logs, and implementation plans are preserved in a
  local private archive rather than the public repository.
- In a Git checkout, the public-surface check inspects indexed paths, including
  staged additions. Ignored local data and installed dependencies are outside
  that publication set. Without Git metadata, it checks the exported tree.
- Public screenshots belong under `assets/`.
