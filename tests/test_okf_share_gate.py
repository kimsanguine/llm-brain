"""Share-ready OKF export gate behavior.

These tests exercise the real CLI/file boundary.  The legacy private export
must remain permissive, while the explicit share operation fails closed and
publishes only a complete staged bundle plus a redacted manifest.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).parent.parent / "scripts"
APPROVAL = "I_ACKNOWLEDGE_SHARE_READY_EXPORT"
SENSITIVE = "SECRET-PATTERN-42"


def _page(
    title: str,
    classification: str | None,
    scope: str | None,
    body: str,
    sources: list[str] | None = None,
) -> str:
    frontmatter: dict[str, object] = {"title": title}
    if classification is not None:
        frontmatter["type"] = classification
    if scope is not None:
        frontmatter["scope"] = scope
    if sources is not None:
        frontmatter["sources"] = sources
    return (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
        + "---\n\n"
        + body
        + "\n"
    )


def _make_repo(
    tmp_path: Path,
    *,
    pages: dict[str, str] | None = None,
    base_config: bool = True,
    local_config: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "schema").mkdir()
    for name in ("okf_export.py", "export_graph.py"):
        shutil.copy(SCRIPTS / name, repo / "scripts" / name)

    if base_config:
        config = {
            "exclude_paths": ["business/**", "canvas/**"],
            "exclude_domains": [],
            "exclude_slugs": [],
            "sensitive_patterns": [],
            "share_policy": {
                "approval_value": APPROVAL,
                "allowed_scopes": ["private", "shared"],
                "allowed_classifications": [
                    "business",
                    "concept",
                    "insight",
                    "lecture",
                    "person",
                    "project",
                    "tool",
                ],
            },
        }
        (repo / "schema" / "okf_export.yaml").write_text(
            yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
        )
    if local_config:
        local = {"exclude_slugs": [], "sensitive_patterns": [SENSITIVE]}
        (repo / "schema" / "okf_export.local.yaml").write_text(
            yaml.safe_dump(local, sort_keys=False), encoding="utf-8"
        )

    pages = pages or {
        "concepts/shared.md": _page(
            "Shared concept",
            "concept",
            "shared",
            "A safe public explanation.",
            ["raw/private/shared-source.md", "https://example.com/public"],
        ),
        "people/private.md": _page(
            "Private person",
            "person",
            "private",
            "Private profile.",
            ["raw/people/private.md"],
        ),
        "business/excluded.md": _page(
            "Excluded business",
            "business",
            None,
            "Excluded by structural policy.",
            ["raw/business/excluded.md"],
        ),
    }
    for rel, content in pages.items():
        path = repo / "wiki" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return repo


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/okf_export.py", *args],
        cwd=repo,
        capture_output=True,
        check=False,
        text=True,
    )


def _share(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(repo, "--share", "--approve-share", APPROVAL, *args)


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_legacy_private_export_remains_compatible_without_scope_or_local_config(tmp_path):
    """Removing the share branch must not tighten the legacy default export."""
    repo = _make_repo(
        tmp_path,
        pages={
            "concepts/legacy.md": _page(
                "Legacy", "concept", None, "Legacy private export content."
            )
        },
        local_config=False,
    )

    result = _run(repo)

    assert result.returncode == 0, result.stderr
    assert (repo / "okf" / "concepts" / "legacy.md").is_file()
    assert not (repo / "okf" / "share-manifest.json").exists()


@pytest.mark.parametrize("approval_args", [(), ("--approve-share", "WRONG")])
def test_share_requires_exact_explicit_human_approval(tmp_path, approval_args):
    """Bypassing the required acknowledgement must fail before publication."""
    repo = _make_repo(tmp_path)

    result = _run(repo, "--share", *approval_args)

    assert result.returncode != 0
    assert "approval" in (result.stdout + result.stderr).lower()
    assert not (repo / "okf-share").exists()


def test_approval_value_without_explicit_share_operation_cannot_export(tmp_path):
    """Removing the --share requirement must not fall through to private export."""
    repo = _make_repo(tmp_path)

    result = _run(repo, "--approve-share", APPROVAL)

    assert result.returncode != 0
    assert "requires --share" in (result.stdout + result.stderr).lower()
    assert not (repo / "okf").exists()
    assert not (repo / "okf-share").exists()


@pytest.mark.parametrize("missing", ["base", "local"])
def test_share_hard_stops_when_security_or_policy_config_is_absent(tmp_path, missing):
    """Removing either required policy layer must make share export fail closed."""
    repo = _make_repo(
        tmp_path,
        base_config=missing != "base",
        local_config=missing != "local",
    )

    result = _share(repo)

    assert result.returncode != 0
    assert "required config" in (result.stdout + result.stderr).lower()
    assert not (repo / "okf-share").exists()


@pytest.mark.parametrize("scope", [None, "unknown-team-scope"])
def test_share_hard_stops_when_candidate_scope_is_absent_or_unknown(tmp_path, scope):
    """Weakening candidate-scope validation must make this test publish a bad page."""
    repo = _make_repo(
        tmp_path,
        pages={
            "concepts/candidate.md": _page(
                "Candidate", "concept", scope, "Candidate content."
            )
        },
    )

    result = _share(repo)

    assert result.returncode != 0
    assert "scope" in (result.stdout + result.stderr).lower()
    assert not (repo / "okf-share").exists()


def test_share_hard_stops_on_unknown_classification(tmp_path):
    """A classification outside the configured allow-list is a policy failure."""
    repo = _make_repo(
        tmp_path,
        pages={
            "concepts/candidate.md": _page(
                "Candidate", "confidential-new-kind", "shared", "Candidate content."
            )
        },
    )

    result = _share(repo)

    assert result.returncode != 0
    assert "classification" in (result.stdout + result.stderr).lower()
    assert not (repo / "okf-share").exists()


def test_share_hard_stops_on_sensitive_hit_without_leaking_detail(tmp_path):
    """A sensitive hit must block output without echoing content or the matched pattern."""
    repo = _make_repo(
        tmp_path,
        pages={
            "concepts/candidate.md": _page(
                "Candidate", "concept", "shared", f"Do not publish {SENSITIVE}."
            )
        },
    )

    result = _share(repo)
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "sensitive" in combined.lower()
    assert SENSITIVE not in combined
    assert "Do not publish" not in combined
    assert not (repo / "okf-share").exists()


def test_share_scans_public_frontmatter_for_sensitive_hits(tmp_path):
    """Dropping rendered-frontmatter scanning must not publish a sensitive title."""
    repo = _make_repo(
        tmp_path,
        pages={
            "concepts/candidate.md": _page(
                f"Candidate {SENSITIVE}", "concept", "shared", "Otherwise safe content."
            )
        },
    )

    result = _share(repo)
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "sensitive" in combined.lower()
    assert SENSITIVE not in combined
    assert not (repo / "okf-share").exists()


def test_share_scans_public_bundle_paths_for_sensitive_hits(tmp_path):
    """Dropping output-path scanning must not publish a sensitive slug."""
    repo = _make_repo(
        tmp_path,
        pages={
            f"concepts/{SENSITIVE.lower()}.md": _page(
                "Safe title", "concept", "shared", "Otherwise safe content."
            )
        },
    )

    result = _share(repo)
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "sensitive" in combined.lower()
    assert SENSITIVE not in combined
    assert SENSITIVE.lower() not in combined
    assert not (repo / "okf-share").exists()


def test_share_rejects_malformed_local_config_without_echoing_sensitive_text(tmp_path):
    """A YAML parser failure must be sanitized before reaching the CLI boundary."""
    repo = _make_repo(tmp_path)
    (repo / "schema" / "okf_export.local.yaml").write_text(
        f"sensitive_patterns:\n  - [{SENSITIVE}\n", encoding="utf-8"
    )

    result = _share(repo)
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "required config is invalid" in combined.lower()
    assert SENSITIVE not in combined
    assert "traceback" not in combined.lower()
    assert not (repo / "okf-share").exists()


def test_safe_share_writes_complete_bundle_and_redacted_deterministic_manifest(tmp_path):
    """Changing manifest aggregation/redaction or publishing partially breaks this contract."""
    repo = _make_repo(tmp_path)

    first = _share(repo)

    assert first.returncode == 0, first.stderr
    out = repo / "okf-share"
    assert (out / ".okf-bundle").is_file()
    assert (out / ".okf-share-bundle").is_file()
    assert (out / "concepts" / "shared.md").is_file()
    assert not (out / "people").exists()
    assert not (out / "business").exists()

    manifest_path = out / "share-manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest == {
        "classification_counts": {
            "excluded": {"business": 1, "person": 1},
            "included": {"concept": 1},
        },
        "config_fingerprint": manifest["config_fingerprint"],
        "counts": {"excluded": 2, "included": 1},
        "operation": "share-ready",
        "schema_version": "1",
        "scope_counts": {"absent": 1, "private": 1, "shared": 1},
        "source_counts": {
            "excluded": {"pages_with_sources": 2, "references": 2},
            "included": {"pages_with_sources": 1, "references": 2},
        },
    }
    assert manifest["config_fingerprint"].startswith("sha256:")
    assert len(manifest["config_fingerprint"]) == len("sha256:") + 64

    published_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in out.rglob("*")
        if path.is_file()
    )
    for forbidden in (
        SENSITIVE,
        "raw/private/shared-source.md",
        "raw/people/private.md",
        "raw/business/excluded.md",
        "Private profile",
        "Excluded by structural policy",
        APPROVAL,
    ):
        assert forbidden not in published_text
    assert "x-llmbrain-" not in (out / "concepts" / "shared.md").read_text(
        encoding="utf-8"
    )

    second = _share(repo)
    assert second.returncode == 0, second.stderr
    assert manifest_path.read_bytes() == manifest_bytes


def test_failed_reshare_preserves_existing_complete_share_bundle(tmp_path):
    """A failed second gate must not delete or partly replace the prior public bundle."""
    repo = _make_repo(tmp_path)
    assert _share(repo).returncode == 0
    out = repo / "okf-share"
    before = _snapshot(out)
    page = repo / "wiki" / "concepts" / "shared.md"
    page.write_text(page.read_text(encoding="utf-8") + SENSITIVE, encoding="utf-8")

    result = _share(repo)

    assert result.returncode != 0
    assert _snapshot(out) == before


def test_staging_write_failure_leaves_no_public_output_or_temp_bundle(tmp_path, monkeypatch):
    """A mid-stage write exception must be contained outside the publication path."""
    repo = _make_repo(tmp_path)
    sys.path.insert(0, str(repo / "scripts"))
    try:
        import okf_export

        share_export = getattr(okf_export, "export_share_bundle", None)
        assert callable(share_export), "share export API is not implemented"

        def fail_root_index(_out_dir, _rendered):
            raise OSError("injected staged write failure")

        monkeypatch.setattr(okf_export, "_write_root_index", fail_root_index)
        out = repo / "public"
        with pytest.raises(OSError, match="injected staged write failure"):
            share_export(
                repo / "wiki",
                out,
                config_path=repo / "schema" / "okf_export.yaml",
                local_config_paths=[repo / "schema" / "okf_export.local.yaml"],
                approval=APPROVAL,
            )
        assert not out.exists()
        assert not list(repo.glob(".public.stage-*"))
    finally:
        sys.path.remove(str(repo / "scripts"))
        sys.modules.pop("okf_export", None)
