"""test_okf_security.py — exclude 보안 경계 회귀 (적대검증 B1·B2·B3·Y1·Y4·Y2).

public 커밋(one-way door)에서 business 누출을 막는 불변식을 고정한다. 적대검증이
찾아낸 누출 경로(중첩 경로·대소문자·별칭 승격·stale 파일)를 각각 재현·차단 검증.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import okf_export  # noqa: E402


def _page(title, type_="concept", body="", extra_fm=""):
    fm = f"title: {title}\ntype: {type_}\nupdated: 2026-06-01\n{extra_fm}"
    return f"---\n{fm}---\n\n# {title}\n\n{body}\n"


def _write(wiki: Path, rel: str, content: str):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_nested_business_excluded(tmp_path):
    """B1: 중첩 경로(archive/business/, projects/x/business/)도 business/**로 제외돼야."""
    wiki = tmp_path / "wiki"
    _write(wiki, "business/anthropic.md", _page("Anthropic"))
    _write(wiki, "archive/business/old-deal.md", _page("Old Deal"))
    _write(wiki, "projects/p1/business/secret.md", _page("Secret"))
    _write(wiki, "concepts/clean.md", _page("Clean"))

    stats = okf_export.export_bundle(wiki, tmp_path / "okf")
    out = tmp_path / "okf"
    assert not (out / "business").exists()
    assert not (out / "archive" / "business").exists()
    assert not (out / "projects" / "p1" / "business").exists()
    # 어떤 출력 파일에도 business 경로가 없어야 (out 기준 상대경로로 판정 — tmp_path명 오탐 회피)
    assert not any(
        "business" in p.relative_to(out).as_posix().lower() for p in out.rglob("*.md")
    )
    assert (out / "concepts" / "clean.md").exists()


def test_case_variant_business_excluded(tmp_path):
    """B2: 대소문자만 다른 Business/·BUSINESS/도 제외돼야 (macOS APFS case-insensitive)."""
    wiki = tmp_path / "wiki"
    _write(wiki, "Business/anthropic.md", _page("Anthropic Upper"))
    _write(wiki, "concepts/clean.md", _page("Clean"))

    okf_export.export_bundle(wiki, tmp_path / "okf")
    out = tmp_path / "okf"
    assert not any(
        "business" in p.relative_to(out).as_posix().lower() for p in out.rglob("*.md")
    )
    # 루트 index.md 목차에도 누출 없어야
    idx = (out / "index.md").read_text(encoding="utf-8")
    assert "Anthropic Upper" not in idx


def test_alias_to_excluded_page_redacted(tmp_path):
    """B3: 제외 페이지를 가리키던 별칭의 민감 텍스트가 본문·description으로 새면 안 됨."""
    wiki = tmp_path / "wiki"
    _write(wiki, "business/anthropic.md", _page("Anthropic", type_="business"))
    _write(
        wiki,
        "concepts/deal.md",
        _page("Deal", body="자세한 건 [[anthropic|Anthropic과 100억 인수협상 진행중]] 참고."),
    )

    stats = okf_export.export_bundle(wiki, tmp_path / "okf")
    text = (tmp_path / "okf" / "concepts" / "deal.md").read_text(encoding="utf-8")

    # 민감 별칭 텍스트가 본문·frontmatter 어디에도 없어야
    assert "100억 인수협상" not in text
    # 링크는 ghost가 아니라 excluded_link_refs로 분류 (Y1)
    assert ("concepts/deal.md", "anthropic") in stats.excluded_link_refs
    assert ("concepts/deal.md", "anthropic") not in stats.broken_links


def test_ghost_vs_excluded_classification(tmp_path):
    """Y1: 진짜 ghost와 제외-타깃 링크가 분리 집계돼야 (보안 게이트 신뢰성)."""
    wiki = tmp_path / "wiki"
    _write(wiki, "business/openai.md", _page("OpenAI", type_="business"))
    _write(
        wiki,
        "concepts/a.md",
        _page("A", body="[[openai]] 그리고 [[정말없는페이지]]."),
    )

    stats = okf_export.export_bundle(wiki, tmp_path / "okf")
    assert ("concepts/a.md", "openai") in stats.excluded_link_refs
    assert ("concepts/a.md", "정말없는페이지") in stats.broken_links
    # 서로 겹치지 않아야
    assert ("concepts/a.md", "openai") not in stats.broken_links


def test_stale_bundle_cleaned_on_reexport(tmp_path):
    """Y4: 재export 시 이전 번들을 정리해 stale 누출 파일이 남지 않아야."""
    wiki = tmp_path / "wiki"
    _write(wiki, "concepts/keep.md", _page("Keep"))
    _write(wiki, "concepts/leak.md", _page("Leak"))
    out = tmp_path / "okf"

    okf_export.export_bundle(wiki, out)
    assert (out / "concepts" / "leak.md").exists()

    # leak 페이지를 제외하고 재export → stale 파일이 남으면 안 됨
    okf_export.export_bundle(wiki, out, exclude_slugs=["leak"])
    assert (out / "concepts" / "keep.md").exists()
    assert not (out / "concepts" / "leak.md").exists()


def test_reexport_refuses_non_bundle_dir(tmp_path):
    """Y4: OKF 번들이 아닌(중요 파일 있는) 비어있지 않은 디렉토리는 덮어쓰기 거부."""
    wiki = tmp_path / "wiki"
    _write(wiki, "concepts/a.md", _page("A"))
    out = tmp_path / "okf"
    out.mkdir()
    (out / "important.txt").write_text("사용자 파일", encoding="utf-8")

    import pytest
    with pytest.raises(SystemExit):
        okf_export.export_bundle(wiki, out)
    # 사용자 파일은 보존돼야
    assert (out / "important.txt").exists()


def test_refuses_dir_with_indexmd_but_no_sentinel(tmp_path):
    """Y4 회귀: index.md+log.md만으로 OKF 번들로 오인해 rmtree하면 안 됨.

    레포 루트도 index.md·log.md를 둘 다 가지므로, 이 판별이 느슨하면 레포가 삭제된다.
    .okf-bundle 센티넬이 없으면 거부하고 기존 파일을 보존해야 한다.
    """
    wiki = tmp_path / "wiki"
    _write(wiki, "concepts/a.md", _page("A"))
    out = tmp_path / "okf"
    out.mkdir()
    (out / "index.md").write_text("# 레포 핵심 인덱스", encoding="utf-8")
    (out / "log.md").write_text("# 레포 핵심 로그", encoding="utf-8")
    critical = out / "wiki_page.md"
    critical.write_text("절대 삭제되면 안 되는 내용", encoding="utf-8")

    import pytest
    with pytest.raises(SystemExit):
        okf_export.export_bundle(wiki, out)
    assert critical.exists(), "센티넬 없는 디렉토리의 파일이 삭제됨 — rmtree 사고"
    assert critical.read_text(encoding="utf-8") == "절대 삭제되면 안 되는 내용"


def test_refuses_out_dir_that_is_source_or_ancestor(tmp_path):
    """Y4: out_dir이 wiki_dir이거나 그 조상(레포 루트)이면 거부 — `--out .` 사고 방지."""
    wiki = tmp_path / "wiki"
    _write(wiki, "concepts/a.md", _page("A"))

    import pytest
    # out_dir == wiki_dir
    with pytest.raises(SystemExit):
        okf_export.export_bundle(wiki, wiki)
    # out_dir == wiki_dir의 조상(레포 루트 격)
    with pytest.raises(SystemExit):
        okf_export.export_bundle(wiki, tmp_path)
    # 소스 보존
    assert (wiki / "concepts" / "a.md").exists()


def test_dict_fm_value_with_triple_dash_sanitized(tmp_path):
    """Y2: dict 타입 내부필드 값의 '---'도 정리돼 consumer split이 안 깨져야."""
    wiki = tmp_path / "wiki"
    _write(
        wiki,
        "concepts/a.md",
        _page("A", extra_fm="meta:\n  note: 'a --- b'\n"),
    )
    okf_export.export_bundle(wiki, tmp_path / "okf")
    text = (tmp_path / "okf" / "concepts" / "a.md").read_text(encoding="utf-8")
    # frontmatter 블록이 '---' 부분문자열로 안 끊겨야
    _, fm_block, _ = text.split("---", 2)
    assert yaml.safe_load(fm_block) is not None
