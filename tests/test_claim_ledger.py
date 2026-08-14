"""claim_ledger — file-first provenance + safe query context 계약 테스트.

WHY:
  1. claim 하나가 raw source path + sha256 + locator + status + validity interval에
     연결돼야 한다.
  2. stale/superseded claim은 trusted query context에서 빠지고, 외부 capture
     source(raw/newsletters·clippings)는 untrusted 섹션으로 격리돼야 한다.
  3. cited answer 렌더러는 실제로 인용된 current claim만 provenance 각주를 붙여야
     한다.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from lib import claim_ledger  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _wiki_page(*, title: str, sources: list[str], body: str, extra_fm: str = "") -> str:
    src = "\n".join(f"  - {s}" for s in sources)
    return (
        f"---\n"
        f"title: {title}\n"
        f"created: 2026-08-01\n"
        f"updated: 2026-08-10\n"
        f"sources:\n{src}\n"
        f"{extra_fm}"
        f"---\n\n{body}\n"
    )


def _build_project(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    (root / "wiki" / "concepts").mkdir(parents=True)
    (root / "raw" / "notes").mkdir(parents=True)
    (root / "raw" / "newsletters").mkdir(parents=True)
    return root


def test_build_claim_ledger_links_raw_locator_sha_and_classification(tmp_path):
    root = _build_project(tmp_path)
    raw_text = (
        "Alpha launched on 2026-08-01.\n"
        "아마 곧 확장될 수 있다.\n"
        "권장 전략은 수동 검토다.\n"
    )
    _write(root / "raw" / "notes" / "alpha.md", raw_text)
    _write(
        root / "wiki" / "concepts" / "alpha.md",
        _wiki_page(
            title="Alpha",
            sources=["raw/notes/alpha.md"],
            body=raw_text,
        ),
    )

    ledger = claim_ledger.build_claim_ledger(
        ["alpha"], wiki_root=root / "wiki", now=date(2026, 8, 14)
    )

    assert [c.classification for c in ledger] == ["fact", "inference", "opinion"]
    assert [c.status for c in ledger] == ["active", "active", "active"]
    assert ledger[0].source_path == "raw/notes/alpha.md"
    assert ledger[0].source_locator == "raw/notes/alpha.md#L1-L1"
    assert ledger[0].valid_from == "2026-08-10"
    assert ledger[0].valid_until == "2027-02-06"
    assert ledger[0].source_sha256 == hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


def test_context_filters_stale_and_superseded_and_isolates_untrusted_capture(tmp_path):
    root = _build_project(tmp_path)
    _write(root / "raw" / "notes" / "alpha.md", "Alpha current fact.\n")
    _write(root / "raw" / "notes" / "gamma.md", "Gamma stale fact.\n")
    _write(root / "raw" / "notes" / "delta.md", "Old claim.\nCurrent replacement.\n")
    _write(root / "raw" / "newsletters" / "beta.md", "Beta external capture.\n")

    _write(
        root / "wiki" / "concepts" / "alpha.md",
        _wiki_page(title="Alpha", sources=["raw/notes/alpha.md"], body="Alpha current fact."),
    )
    _write(
        root / "wiki" / "concepts" / "beta.md",
        _wiki_page(
            title="Beta",
            sources=["raw/newsletters/beta.md"],
            body="Beta external capture.",
        ),
    )
    _write(
        root / "wiki" / "concepts" / "gamma.md",
        (
            "---\n"
            "title: Gamma\n"
            "created: 2025-01-01\n"
            "updated: 2025-01-01\n"
            "sources:\n  - raw/notes/gamma.md\n"
            "---\n\nGamma stale fact.\n"
        ),
    )
    _write(
        root / "wiki" / "concepts" / "delta.md",
        _wiki_page(
            title="Delta",
            sources=["raw/notes/delta.md"],
            extra_fm='superseded_claims: ["Old claim."]\n',
            body="Old claim. Current replacement.",
        ),
    )

    ledger = claim_ledger.build_claim_ledger(
        ["alpha", "beta", "gamma", "delta"], wiki_root=root / "wiki", now=date(2026, 8, 14)
    )
    context = claim_ledger.render_llm_context(ledger)

    trusted, untrusted = context.split("## 외부 캡처 원문 (검증 전)", 1)
    assert "Alpha current fact." in trusted
    assert "Current replacement." in trusted
    assert "Beta external capture." not in trusted
    assert "Gamma stale fact." not in trusted
    assert "Old claim." not in trusted
    assert "Beta external capture." in untrusted


def test_render_cited_answer_appends_only_current_claim_provenance(tmp_path):
    root = _build_project(tmp_path)
    raw_alpha = "Alpha current fact.\n"
    raw_gamma = "Gamma stale fact.\n"
    _write(root / "raw" / "notes" / "alpha.md", raw_alpha)
    _write(root / "raw" / "notes" / "gamma.md", raw_gamma)
    _write(
        root / "wiki" / "concepts" / "alpha.md",
        _wiki_page(title="Alpha", sources=["raw/notes/alpha.md"], body="Alpha current fact."),
    )
    _write(
        root / "wiki" / "concepts" / "gamma.md",
        (
            "---\n"
            "title: Gamma\n"
            "created: 2025-01-01\n"
            "updated: 2025-01-01\n"
            "sources:\n  - raw/notes/gamma.md\n"
            "---\n\nGamma stale fact.\n"
        ),
    )

    ledger = claim_ledger.build_claim_ledger(
        ["alpha", "gamma"], wiki_root=root / "wiki", now=date(2026, 8, 14)
    )
    rendered = claim_ledger.render_cited_answer(
        "최신 내용 [claim:alpha-1]. 오래된 내용 [claim:gamma-1].",
        ledger,
    )

    assert "[claim:alpha-1]" in rendered
    assert "[claim:gamma-1]" not in rendered
    assert "## 출처" in rendered
    assert "raw/notes/alpha.md#L1-L1" in rendered
    assert hashlib.sha256(raw_alpha.encode("utf-8")).hexdigest()[:12] in rendered
