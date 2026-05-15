#!/usr/bin/env python3
"""
curate.py — wiki 감사(audit) + 압축(distill) + 수명 관리(lifecycle).

사용법:
  python scripts/curate.py --all
  python scripts/curate.py --audit
  python scripts/curate.py --distill
  python scripts/curate.py --lifecycle
"""
import argparse
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import yaml

WIKI_ROOT = Path(__file__).parent.parent
WIKI_DIR = WIKI_ROOT / "wiki"
SCHEMA_DIR = WIKI_ROOT / "schema"
LOG_FILE = WIKI_ROOT / "log.md"
REPORT_FILE = WIKI_DIR / "curate_report.md"
# lifecycle 제외 도메인 (ttl_days: 0인 것들)
LIFECYCLE_EXEMPT = {"concepts", "tools", "people", "projects", "business", "lecture"}


# ── Audit ─────────────────────────────────────────────────────────────

def find_all_wiki_pages() -> list[Path]:
    return [p for p in WIKI_DIR.rglob("*.md")
            if p.name not in ("curate_report.md",) and "archive" not in p.parts]


def extract_wikilinks(content: str) -> set[str]:
    return set(re.findall(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]", content))


def build_link_graph(pages: list[Path]) -> tuple[dict, dict]:
    outbound: dict[str, set[str]] = {}
    inbound: dict[str, set[str]] = defaultdict(set)
    page_names = {p.stem for p in pages}

    for page in pages:
        name = page.stem
        links = extract_wikilinks(page.read_text())
        valid = links & page_names
        outbound[name] = valid
        for target in valid:
            inbound[target].add(name)

    return outbound, dict(inbound)


def run_audit(pages: list[Path]) -> dict:
    _, inbound = build_link_graph(pages)
    now = datetime.now()

    orphans, stale_links, contradictions = [], [], []

    for page in pages:
        name = page.stem
        mtime = datetime.fromtimestamp(page.stat().st_mtime)
        age_days = (now - mtime).days
        in_count = len(inbound.get(name, set()))

        if in_count == 0 and age_days > 30:
            orphans.append({
                "path": str(page.relative_to(WIKI_ROOT)),
                "age_days": age_days,
                "inbound": 0,
            })

    # Stale link 탐지
    page_names = {p.stem for p in pages}
    for page in pages:
        content = page.read_text()
        links = extract_wikilinks(content)
        missing = links - page_names
        for m in missing:
            stale_links.append({
                "source": str(page.relative_to(WIKI_ROOT)),
                "missing_target": m,
            })

    return {"orphans": orphans, "stale_links": stale_links, "contradictions": contradictions}


# ── Distill ────────────────────────────────────────────────────────────

def run_distill(pages: list[Path]) -> list[str]:
    """
    distill은 Claude Code (claude CLI)가 담당한다.
    이 함수는 distill 대상 파일 목록만 반환하고,
    실제 실행은 run_daily.sh에서 claude -p 로 위임된다.
    """
    insight_candidates = [p for p in pages if "insights" in str(p)]
    if len(insight_candidates) < 3:
        print("  [distill] insight 페이지 3개 미만 — 건너뜀")
        return []

    paths = [str(p.relative_to(WIKI_ROOT)) for p in insight_candidates]
    print(f"  [distill] {len(paths)}개 insight 페이지 → claude distill 위임")
    # run_daily.sh가 이 출력을 보고 claude -p "curate --distill 해줘" 실행
    return paths


# ── Lifecycle ──────────────────────────────────────────────────────────

def run_lifecycle(pages: list[Path]) -> dict:
    config = yaml.safe_load((SCHEMA_DIR / "sources.yaml").read_text())
    lifecycle = config.get("lifecycle", {})
    now = datetime.now()
    _, inbound = build_link_graph(pages)

    archive_candidates, delete_candidates = [], []

    for page in pages:
        domain = page.parent.name
        if domain in LIFECYCLE_EXEMPT:
            continue

        domains_cfg = lifecycle.get("domains", {})
        ttl = domains_cfg.get(domain, {})
        ttl_days = ttl if isinstance(ttl, int) else ttl.get("ttl_days", 0)
        if ttl_days == 0:
            continue

        mtime = datetime.fromtimestamp(page.stat().st_mtime)
        age_days = (now - mtime).days
        in_count = len(inbound.get(page.stem, set()))

        if age_days > ttl_days and in_count == 0:
            archive_candidates.append({
                "path": str(page.relative_to(WIKI_ROOT)),
                "age_days": age_days,
                "inbound": in_count,
            })
        if age_days > ttl_days * 2 and in_count <= 1:
            delete_candidates.append({
                "path": str(page.relative_to(WIKI_ROOT)),
                "age_days": age_days,
                "inbound": in_count,
            })

    return {"archive": archive_candidates, "delete": delete_candidates}


# ── Report ─────────────────────────────────────────────────────────────

def write_report(audit: dict, distilled: list, lifecycle: dict) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# Curate Report — {now}\n"]

    lines.append("## Audit 결과")
    orphans = audit.get("orphans", [])
    lines.append(f"### Orphan 페이지 ({len(orphans)}개)")
    for o in orphans:
        lines.append(f"- {o['path']} — {o['age_days']}일 경과, inbound 0")

    stale = audit.get("stale_links", [])
    lines.append(f"\n### Stale 링크 ({len(stale)}개)")
    for s in stale:
        lines.append(f"- {s['source']} → [[{s['missing_target']}]] (페이지 없음)")

    lines.append(f"\n## Distill 결과")
    lines.append(f"- 생성된 insights 페이지: {len(distilled)}개")
    for d in distilled:
        lines.append(f"  - {d}")

    lines.append("\n## Lifecycle 후보 (사용자 확인 필요)")
    archive = lifecycle.get("archive", [])
    lines.append(f"### Archive 후보 ({len(archive)}개)")
    for a in archive:
        lines.append(f"- {a['path']} — {a['age_days']}일 경과, inbound {a['inbound']}")

    delete = lifecycle.get("delete", [])
    lines.append(f"\n### Delete 후보 ({len(delete)}개)")
    for d in delete:
        lines.append(f"- {d['path']} — {d['age_days']}일 경과, inbound {d['inbound']}")
    if delete:
        lines.append("\n> 삭제 실행: `python scripts/curate.py --purge`")

    REPORT_FILE.write_text("\n".join(lines))
    print(f"\n[curate] 리포트 저장: wiki/curate_report.md")

    log_entry = (
        f"\n## {now} [curate]\n"
        f"- orphan: {len(orphans)}개\n"
        f"- stale_links: {len(stale)}개\n"
        f"- distilled: {len(distilled)}개\n"
        f"- archive 후보: {len(archive)}개\n"
    )
    LOG_FILE.open("a").write(log_entry)


def do_purge() -> None:
    """curate_report.md의 Archive 후보를 wiki/archive/로 이동."""
    if not REPORT_FILE.exists():
        print("[purge] curate_report.md 없음. curate --lifecycle 먼저 실행.")
        return
    content = REPORT_FILE.read_text()
    archive_dir = WIKI_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)
    moved = 0
    for match in re.finditer(r"- (wiki/\S+\.md)", content):
        src = WIKI_ROOT / match.group(1)
        if src.exists():
            dst = archive_dir / src.name
            src.rename(dst)
            print(f"  [archive] {match.group(1)}")
            moved += 1
    print(f"[purge] {moved}개 파일 archive/로 이동")


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM wiki curate")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--distill", action="store_true")
    parser.add_argument("--lifecycle", action="store_true")
    parser.add_argument("--purge", action="store_true", help="archive 후보 실제 이동")
    args = parser.parse_args()

    if args.purge:
        do_purge()
        return

    run_all = args.all or not any([args.audit, args.distill, args.lifecycle])
    pages = find_all_wiki_pages()
    print(f"[curate] {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(pages)}개 페이지 분석")

    audit_result = run_audit(pages) if (run_all or args.audit) else {}
    distilled = run_distill(pages) if (run_all or args.distill) else []
    lifecycle_result = run_lifecycle(pages) if (run_all or args.lifecycle) else {}

    write_report(audit_result, distilled, lifecycle_result)


if __name__ == "__main__":
    main()
