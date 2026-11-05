"""Public repository boundaries must stay enforceable in a fresh clone."""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from public_surface import violations  # noqa: E402


def test_rejects_docs_and_archive_at_any_depth(tmp_path):
    (tmp_path / "nested" / "docs").mkdir(parents=True)
    (tmp_path / "history" / ".archive").mkdir(parents=True)

    assert violations(tmp_path) == {"history/.archive", "nested/docs"}


def test_ignores_local_worktrees(tmp_path):
    (tmp_path / ".worktrees" / "scratch" / "docs").mkdir(parents=True)

    assert violations(tmp_path) == set()


def test_git_checkout_checks_publishable_index_instead_of_private_local_data(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'public.py').write_text('pass\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', 'public.py'], check=True)
    for directory in ('docs/research', 'raw/docs', 'tools/node_modules/library/docs'):
        (tmp_path / directory).mkdir(parents=True)
        (tmp_path / directory / 'private.md').write_text('local only\n')

    assert violations(tmp_path) == set()


def test_git_checkout_rejects_forbidden_paths_staged_for_publication(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'nested' / 'docs').mkdir(parents=True)
    (tmp_path / 'nested' / 'docs' / 'private.md').write_text('must not publish\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', 'nested/docs/private.md'], check=True)

    assert violations(tmp_path) == {'nested/docs'}


@pytest.mark.parametrize('name', ['docs', '.archive'])
def test_git_checkout_rejects_indexed_forbidden_directory_symlinks(tmp_path, name):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'target').mkdir()
    (tmp_path / name).symlink_to('target', target_is_directory=True)
    subprocess.run(['git', '-C', str(tmp_path), 'add', '-f', name], check=True)

    assert violations(tmp_path) == {name}


def test_current_public_tree_has_no_forbidden_directories():
    assert violations(ROOT) == set()
