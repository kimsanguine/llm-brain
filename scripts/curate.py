#!/usr/bin/env python3
"""
curate.py — wiki 감사(audit) + 압축(distill) + 수명 관리(lifecycle) + 링크 분석(graph).

사용법:
  python scripts/curate.py --all
  python scripts/curate.py --audit
  python scripts/curate.py --distill
  python scripts/curate.py --lifecycle
  python scripts/curate.py --graph
"""
import argparse
import json
import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

WIKI_ROOT = Path(__file__).parent.parent
WIKI_DIR = WIKI_ROOT / "wiki"
SCHEMA_DIR = WIKI_ROOT / "schema"
LOG_FILE = WIKI_ROOT / "log.md"
REPORT_FILE = WIKI_DIR / "curate_report.md"
DISTILL_QUEUE_FILE = WIKI_DIR / "distill_queue.md"
WIKI_STATS_FILE = WIKI_ROOT / "wiki_stats.json"
# lifecycle 제외 도메인 (ttl_days: 0인 것들)
LIFECYCLE_EXEMPT = {"concepts", "tools", "people", "projects", "business", "lecture"}


# ── Stats (access tracking) ────────────────────────────────────────────

def load_wiki_stats() -> dict:
    """wiki_stats.json 로드. 없으면 빈 dict 반환."""
    if WIKI_STATS_FILE.exists():
        return json.loads(WIKI_STATS_FILE.read_text())
    return {}


def save_wiki_stats(stats: dict) -> None:
    WIKI_STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2))


def record_access(page_slug: str) -> None:
    """query 모드에서 호출. page_slug에 대한 access_count를 wiki_stats.json에 기록."""
    stats = load_wiki_stats()
    entry = stats.get(page_slug, {"access_count": 0, "last_accessed": None})
    entry["access_count"] += 1
    entry["last_accessed"] = datetime.now().strftime("%Y-%m-%d")
    stats[page_slug] = entry
    save_wiki_stats(stats)
    print(f"  [stats] {page_slug} access_count={entry['access_count']}")


# ── Frontmatter helpers ────────────────────────────────────────────────

_FM_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


class FrontmatterParseError(ValueError):
    """frontmatter 블록은 있으나 YAML 파싱에 실패했을 때 raise.

    fail-loud: 조용히 ({}, body)를 반환하면 호출부가 "frontmatter 없음"으로 오인해
    기존 필드(title·type·tags·created·sources 등)를 덮어써 영구 삭제하는
    silent data-loss가 발생한다. 그래서 파싱 실패를 명확히 신호한다.
    """


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """(frontmatter_dict, body) 반환. frontmatter 없으면 ({}, content).

    frontmatter 블록은 존재하나 YAML이 invalid면 FrontmatterParseError를 raise한다
    (조용한 {} 반환 금지 — 호출부의 덮어쓰기로 인한 데이터 손실 방지).
    """
    m = _FM_PATTERN.match(content)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterParseError(str(exc)) from exc
    body = content[m.end():]
    return fm, body


def serialize_frontmatter(fm: dict, body: str) -> str:
    dumped = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{dumped}---{body}"


def ensure_distill_fields(page: Path) -> dict:
    """
    distill_level / access_count / last_accessed / last_distilled 필드가
    없으면 기본값으로 추가하고 파일을 갱신한다. 갱신된 frontmatter 반환.

    frontmatter YAML 파싱에 실패한 페이지는 절대 rewrite하지 않는다
    (skip + warning). 빈 fm을 다시 써버리면 기존 필드가 영구 삭제되므로,
    원본을 그대로 보존하고 빈 dict를 반환한다.
    """
    content = page.read_text()
    try:
        fm, body = parse_frontmatter(content)
    except FrontmatterParseError as exc:
        logger.warning(
            "frontmatter 파싱 실패 — 원본 보존하고 건너뜀: %s (%s)",
            page, exc,
        )
        return {}
    changed = False
    for field, default in [
        ("distill_level", 0),
        ("access_count", 0),
        ("last_accessed", None),
        ("last_distilled", None),
    ]:
        if field not in fm:
            fm[field] = default
            changed = True
    if changed:
        page.write_text(serialize_frontmatter(fm, body))
    return fm


# ── Audit ─────────────────────────────────────────────────────────────

def find_all_wiki_pages() -> list[Path]:
    excluded = {
        "curate_report.md",
        "distill_queue.md",
        "graph_report.md",
    }
    return [p for p in WIKI_DIR.rglob("*.md")
            if p.name not in excluded and "archive" not in p.parts]


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
    wiki 전체를 스캔해 distill 후보를 분류하고 distill_queue.md에 저장한다.
    실제 LLM 압축은 Claude Code가 이 파일을 읽고 실행한다.

    반환값: distill 큐에 추가된 페이지 경로 목록.
    """
    now = datetime.now()
    stats = load_wiki_stats()

    urgent: list[dict] = []    # access_count >= 10 AND distill_level < 3
    priority: list[dict] = []  # access_count >= 5  AND distill_level < 2
    lifecycle_via_distill: list[dict] = []  # access_count == 0 AND 90일+

    for page in pages:
        # frontmatter 필드 보장
        fm = ensure_distill_fields(page)

        # wiki_stats.json의 access_count를 frontmatter와 동기
        slug = page.stem
        stats_entry = stats.get(slug, {})
        stats_access = stats_entry.get("access_count", 0)
        # 둘 중 큰 값을 사용 (두 소스 중 최신 반영)
        access_count = max(fm.get("access_count", 0), stats_access)

        distill_level = fm.get("distill_level", 0)
        created_raw = fm.get("created")
        if created_raw:
            try:
                created_dt = datetime.strptime(str(created_raw), "%Y-%m-%d")
                age_days = (now - created_dt).days
            except ValueError:
                age_days = 0
        else:
            mtime = datetime.fromtimestamp(page.stat().st_mtime)
            age_days = (now - mtime).days

        rel_path = str(page.relative_to(WIKI_ROOT))
        entry = {
            "path": rel_path,
            "slug": slug,
            "distill_level": distill_level,
            "access_count": access_count,
            "age_days": age_days,
        }

        if access_count >= 10 and distill_level < 3:
            urgent.append(entry)
        elif access_count >= 5 and distill_level < 2:
            priority.append(entry)
        elif access_count == 0 and age_days > 90:
            lifecycle_via_distill.append(entry)

    # distill_queue.md 작성
    ts = now.strftime("%Y-%m-%d %H:%M")
    lines = [f"# Distill Queue — {ts}\n",
             "> 이 파일은 `curate --distill`이 생성합니다. Claude Code가 읽고 순서대로 압축을 실행하세요.\n"]

    lines.append(f"\n## 긴급 후보 (access ≥ 10, distill_level < 3) — {len(urgent)}개")
    lines.append("우선순위 1: 즉시 압축 필요\n")
    for e in sorted(urgent, key=lambda x: x["access_count"], reverse=True):
        lines.append(
            f"- [ ] `{e['path']}` — "
            f"access={e['access_count']}, level={e['distill_level']}, age={e['age_days']}일"
        )

    lines.append(f"\n## 우선 후보 (access ≥ 5, distill_level < 2) — {len(priority)}개")
    lines.append("우선순위 2: 다음 사이클에 압축\n")
    for e in sorted(priority, key=lambda x: x["access_count"], reverse=True):
        lines.append(
            f"- [ ] `{e['path']}` — "
            f"access={e['access_count']}, level={e['distill_level']}, age={e['age_days']}일"
        )

    lines.append(f"\n## Lifecycle 후보 (access=0, 90일+) — {len(lifecycle_via_distill)}개")
    lines.append("우선순위 3: `curate --lifecycle` 또는 삭제 검토\n")
    for e in sorted(lifecycle_via_distill, key=lambda x: x["age_days"], reverse=True):
        lines.append(
            f"- [ ] `{e['path']}` — "
            f"age={e['age_days']}일, access=0"
        )

    DISTILL_QUEUE_FILE.write_text("\n".join(lines))
    total = len(urgent) + len(priority)
    print(f"  [distill] 긴급={len(urgent)}, 우선={len(priority)}, lifecycle={len(lifecycle_via_distill)} → wiki/distill_queue.md 저장")

    all_candidates = [e["path"] for e in urgent + priority]
    return all_candidates


# ── Lifecycle ──────────────────────────────────────────────────────────

def _load_sources_config() -> dict:
    """schema/sources.yaml을 읽는다. 없으면 sources.example.yaml로 폴백,
    둘 다 없으면 빈 config로 graceful 진행 (fresh clone에서 크래시 금지)."""
    sources_file = SCHEMA_DIR / "sources.yaml"
    if not sources_file.exists():
        example = SCHEMA_DIR / "sources.example.yaml"
        if example.exists():
            print(f"  [lifecycle] sources.yaml 없음 — {example.name}로 폴백")
            sources_file = example
        else:
            print("  [lifecycle] sources.yaml/sources.example.yaml 모두 없음 — lifecycle 건너뜀")
            return {}
    return yaml.safe_load(sources_file.read_text()) or {}


def run_lifecycle(pages: list[Path]) -> dict:
    config = _load_sources_config()
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
    lines.append(f"- 큐에 추가된 페이지: {len(distilled)}개")
    for d in distilled:
        lines.append(f"  - {d}")
    if distilled:
        lines.append("\n> 상세 큐: `wiki/distill_queue.md`")

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
        f"- distill 큐: {len(distilled)}개\n"
        f"- archive 후보: {len(archive)}개\n"
    )
    LOG_FILE.open("a").write(log_entry)


# ── Graph Health ──────────────────────────────────────────────────────

def graph_health() -> None:
    """
    wiki/graph.json을 읽어 그래프 건강 지표를 출력한다.
    - pages, wikilink edges, avg degree, components, diameter, avg shortest
    - low-degree (≤2) 페이지 수, ghost 수
    - 카테고리별 내부/외부 연결 응집도
    - Betweenness Centrality TOP 5
    """
    import json
    import networkx as nx
    from collections import defaultdict, Counter

    graph_path = WIKI_ROOT / "wiki" / "graph.json"
    if not graph_path.exists():
        print("[health] graph.json 없음 — export_graph 먼저 실행")
        return

    g = json.loads(graph_path.read_text())
    pages = {n["id"]: n for n in g["nodes"] if n["kind"] == "page"}
    ghosts = [n for n in g["nodes"] if n["kind"] == "ghost"]

    G = nx.Graph()
    for p in pages:
        G.add_node(p)
    for l in g["links"]:
        if l["kind"] == "wikilink" and l["source"] in pages and l["target"] in pages:
            G.add_edge(l["source"], l["target"])

    n_pages = G.number_of_nodes()
    n_edges = G.number_of_edges()
    avg_degree = (2 * n_edges / n_pages) if n_pages > 0 else 0
    low_degree = sum(1 for _, d in G.degree() if d <= 2)
    components = nx.number_connected_components(G)

    # 연결 그래프의 지름 / 평균 최단거리 (가장 큰 컴포넌트 기준)
    largest_cc = max(nx.connected_components(G), key=len)
    sub = G.subgraph(largest_cc)
    diameter = nx.diameter(sub)
    avg_shortest = nx.average_shortest_path_length(sub)

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[health] {today}")
    print(f"  pages           = {n_pages}")
    print(f"  wikilink edges  = {n_edges}")
    print(f"  avg degree      = {avg_degree:.2f}")
    print(f"  components      = {components}")
    print(f"  diameter        = {diameter}")
    print(f"  avg shortest    = {avg_shortest:.2f}")
    print(f"  low-degree (≤2) = {low_degree}개")
    print(f"  ghost           = {len(ghosts)}개")

    # 카테고리별 응집도
    print(f"\n[health] 카테고리별 응집도")
    cat_nodes: dict[str, list[str]] = defaultdict(list)
    for pid, pdata in pages.items():
        cat = pdata.get("category", "기타")
        cat_nodes[cat].append(pid)

    cat_node_set: dict[str, set[str]] = {c: set(ns) for c, ns in cat_nodes.items()}
    for cat in sorted(cat_nodes.keys()):
        members = cat_node_set[cat]
        internal = 0
        external = 0
        for u, v in G.edges():
            u_in = u in members
            v_in = v in members
            if u_in and v_in:
                internal += 1
            elif u_in or v_in:
                external += 1
        total = internal + external
        ratio = int(internal / total * 100) if total > 0 else 0
        print(f"  {cat:<12} {len(members):>2}p  internal={internal} external={external}  내부={ratio}%")

    # Betweenness Centrality TOP 5
    print(f"\n[health] Betweenness centrality TOP 5")
    bc = nx.betweenness_centrality(G, normalized=True)
    top5 = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:5]
    for slug, score in top5:
        print(f"  {slug:<40} BC={score:.4f}")


# ── Suggest Bridges ────────────────────────────────────────────────────

def suggest_bridges(n: int) -> None:
    """
    betweenness centrality + structural hole 기반으로 missing link N개를 추천한다.
    - 같은 카테고리 페이지 쌍은 제외
    - 두 페이지 사이 hop이 2 이상 (직접 연결 안 됨)
    - inbound 합 + betweenness 합 기준으로 상위 N개 선정
    """
    import json
    import networkx as nx
    from itertools import combinations

    graph_path = WIKI_ROOT / "wiki" / "graph.json"
    if not graph_path.exists():
        print("[suggest-bridges] graph.json 없음 — export_graph 먼저 실행")
        return

    g = json.loads(graph_path.read_text())
    pages = {n["id"]: n for n in g["nodes"] if n["kind"] == "page"}

    G = nx.Graph()
    for p in pages:
        G.add_node(p)
    for l in g["links"]:
        if l["kind"] == "wikilink" and l["source"] in pages and l["target"] in pages:
            G.add_edge(l["source"], l["target"])

    bc = nx.betweenness_centrality(G, normalized=True)

    # 연결된 페이지 쌍만 대상으로 경로 계산 (가장 큰 컴포넌트)
    largest_cc = max(nx.connected_components(G), key=len)
    sub = G.subgraph(largest_cc)
    sub_pages = list(largest_cc)

    candidates = []
    for a, b in combinations(sub_pages, 2):
        # 같은 카테고리 제외
        if pages[a].get("category") == pages[b].get("category"):
            continue
        # 이미 직접 연결된 쌍 제외
        if sub.has_edge(a, b):
            continue
        # hop distance 계산
        try:
            hop = nx.shortest_path_length(sub, a, b)
        except nx.NetworkXNoPath:
            continue
        if hop < 2:
            continue

        inbound_a = pages[a].get("inbound", 0)
        inbound_b = pages[b].get("inbound", 0)
        hub_score = inbound_a + inbound_b
        bc_score = bc.get(a, 0) + bc.get(b, 0)
        # 정렬 기준: hub_score 우선, bc_score 보조
        candidates.append((a, b, hop, hub_score, bc_score))

    # hub_score 내림차순, bc_score 내림차순 정렬
    candidates.sort(key=lambda x: (x[3], x[4]), reverse=True)
    top = candidates[:n]

    print(f"[suggest-bridges] 추천 missing link {len(top)}개")
    for i, (a, b, hop, hub_score, bc_score) in enumerate(top, 1):
        print(f"  {i}. [[{a}]] ↔ [[{b}]]  hop={hop}, hub-score={hub_score}")


# ── Purge ──────────────────────────────────────────────────────────────

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
    parser.add_argument("--record-access", metavar="PAGE_SLUG", help="access_count 기록 (query 모드용)")
    parser.add_argument("--health", action="store_true",
                        help="graph health 지표 출력 (avg degree, components, BC top, low-degree count)")
    parser.add_argument("--suggest-bridges", type=int, default=0, metavar="N",
                        help="betweenness/structural-hole 기반 missing link 추천 N개")
    args = parser.parse_args()

    if args.purge:
        do_purge()
        return

    if args.record_access:
        record_access(args.record_access)
        return

    if args.health:
        graph_health()
        return

    if args.suggest_bridges > 0:
        suggest_bridges(args.suggest_bridges)
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
