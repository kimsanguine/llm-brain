#!/usr/bin/env python3
"""memory_health.py — 읽기전용 메모리 건강 리포트 (PRD US-008).

5층 메모리 OS 의 ③ "오프라인 제어(메타 기억)" 관측기. wiki(의미)·episodes(에피소드)·
procedures(절차) 를 **읽기만** 해서 집계 리포트를 wiki/memory_health_report.md 에 쓴다.
의미 기억을 관측만 하고 **절대 wiki 페이지를 이동·삭제·생성하지 않는다**(curate 의
distill/lifecycle/purge 와 구분되는, side-effect-free 진단 도구).

리포트 섹션: 메모리 타입별 페이지 수 · orphan semantic · stale 절차 · 최근 에피소드
(개수 + ts/task_type/status 메타만) · top 재사용 페이지 · 저신뢰 페이지 · archive 후보.

🔴 프라이버시(SPEC §D, Claude#1·Codex C1): episode notes/inputs/outputs/user_goal 같은
verbatim 본문은 **절대** 리포트에 넣지 않는다. 에피소드는 **집계 수치 + 메타(시각·종류·
상태)** 로만 표면화한다. 또 리포트 파일명은 okf_export.META_FILES 에 등재돼(§D 누출 봉인)
공개 OKF 번들로 export 되지 않는다.

curate.py 의 *순수* 헬퍼(compute_memory_score·build_link_graph·build_express_reuse_index·
build_episode_ref_index·load_graph_index)만 재사용한다 — WIKI_ROOT 에 묶인
run_lifecycle/ensure_distill_fields(페이지 rewrite) 는 쓰지 않는다(읽기 전용 보장).
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import curate  # noqa: E402  (순수 헬퍼만 사용 — 쓰기 함수 호출 금지)
import episode  # noqa: E402
import procedures as procedures_mod  # noqa: E402
from lib import frontmatter_utils  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WIKI_ROOT = REPO_ROOT / "wiki"
DEFAULT_EPISODES_DIR = REPO_ROOT / "episodes"
DEFAULT_PROCEDURES_DIR = REPO_ROOT / "procedures"

REPORT_FILENAME = "memory_health_report.md"
# wiki_root 직속 메타·리포트 파일 — 페이지 집계에서 제외(curate.find_all_wiki_pages 와 정합).
_SKIP_META = {"curate_report.md", "distill_queue.md", "graph_report.md", REPORT_FILENAME}
# memory_type 미선언 페이지의 기본값. wiki/ 자체가 의미 기억 층(SPEC §A)이므로 semantic.
_DEFAULT_MEMORY_TYPE = "semantic"

LOW_CONFIDENCE_THRESHOLD = 0.5
STALE_PROCEDURE_DAYS = 180
ARCHIVE_AGE_DAYS = 180
TOP_REUSED_N = 10
RECENT_EPISODE_LIMIT = 50   # 집계 대상 최근 에피소드 수
RECENT_BRIEF_N = 20         # 브리프 ref 로 나열할 최대 줄 수


@dataclass
class _PageInfo:
    path: Path
    rel: str
    slug: str
    fm: dict
    memory_type: str
    confidence: float | None


def _as_float(x) -> float | None:
    """bool/non-numeric 은 None. confidence 판정용."""
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    return None


def _age_days(fm: dict, fallback_path: Path | None, now: datetime) -> int:
    """last_verified > updated > created 순으로 age(일) 계산. 전부 부재 시 mtime fallback.

    frontmatter 날짜가 우선이라 테스트 결정성을 확보한다(now 주입). 파싱 실패/부재면
    다음 키로, 끝내 없으면 파일 mtime(없으면 0).
    """
    if isinstance(fm, dict):
        for key in ("last_verified", "updated", "created"):
            val = fm.get(key)
            if not val:
                continue
            try:
                dt = datetime.strptime(str(val)[:10], "%Y-%m-%d")
            except (ValueError, TypeError):
                continue
            return (now - dt).days
    if fallback_path is not None:
        try:
            mtime = datetime.fromtimestamp(fallback_path.stat().st_mtime)
            return (now - mtime).days
        except OSError:
            return 0
    return 0


def _collect_pages(wiki_root: Path) -> tuple[list[_PageInfo], list[tuple[str, str]]]:
    """wiki_root/**/*.md 를 읽어 _PageInfo 리스트 + 파싱오류 목록 반환(읽기 전용).

    메타·리포트 파일(루트 직속)과 archive/ 하위는 제외한다(curate 의 페이지 정의와 정합).
    frontmatter 파싱 실패는 크래시 대신 fm={} 로 폴백하고 표면화한다(Rule 8).
    """
    pages: list[_PageInfo] = []
    parse_errors: list[tuple[str, str]] = []
    for md in sorted(wiki_root.rglob("*.md")):
        rel = md.relative_to(wiki_root).as_posix()
        if md.parent == wiki_root and md.name in _SKIP_META:
            continue
        if "archive" in md.relative_to(wiki_root).parts:
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            parse_errors.append((rel, f"읽기 실패: {type(exc).__name__}"))
            continue
        try:
            fm, _body = frontmatter_utils.read_fm(text)
        except frontmatter_utils.FrontmatterParseError:
            parse_errors.append((rel, "frontmatter 파싱 실패"))
            fm = {}
        if not isinstance(fm, dict):
            fm = {}
        mt = fm.get("memory_type") or _DEFAULT_MEMORY_TYPE
        pages.append(_PageInfo(
            path=md, rel=rel, slug=md.stem, fm=fm,
            memory_type=str(mt), confidence=_as_float(fm.get("confidence")),
        ))
    return pages, parse_errors


def _section_memory_types(pages: list[_PageInfo]) -> list[str]:
    counts = Counter(p.memory_type for p in pages)
    lines = [f"## 메모리 타입별 페이지 수 — 총 {len(pages)}개", ""]
    for mt in sorted(counts):
        lines.append(f"- {mt}: {counts[mt]}")
    return lines + [""]


def _section_orphans(pages: list[_PageInfo], inbound: dict) -> list[str]:
    orphans = [p for p in pages
               if p.memory_type == "semantic" and not inbound.get(p.slug)]
    lines = [f"## Orphan semantic 페이지 (inbound 0) — {len(orphans)}개", ""]
    for p in sorted(orphans, key=lambda x: x.rel):
        lines.append(f"- {p.slug} (`{p.rel}`)")
    return lines + [""]


def _section_stale_procedures(procedures_dir: Path, now: datetime) -> list[str]:
    stale: list[tuple[str, int]] = []
    for slug in procedures_mod.list_procedures(procedures_dir=procedures_dir):
        try:
            fm, _ = procedures_mod.read_procedure(slug, procedures_dir=procedures_dir)
        except (OSError, frontmatter_utils.FrontmatterParseError):
            continue
        age = _age_days(fm if isinstance(fm, dict) else {},
                        procedures_dir / f"{slug}.md", now)
        if age > STALE_PROCEDURE_DAYS:
            stale.append((slug, age))
    lines = [f"## Stale 절차 (>{STALE_PROCEDURE_DAYS}일 미검증) — {len(stale)}개", ""]
    for slug, age in sorted(stale, key=lambda x: (-x[1], x[0])):
        lines.append(f"- {slug} — {age}일")
    return lines + [""]


def _section_recent_episodes(episodes_dir: Path) -> list[str]:
    """최근 에피소드: 개수 + task_type/status 집계 + ts·종류·상태 브리프(본문 없음).

    🔴 user_goal/inputs/outputs/notes 같은 verbatim 본문은 절대 넣지 않는다(§D).
    """
    recent = episode.read_recent(limit=RECENT_EPISODE_LIMIT, episodes_dir=episodes_dir)
    by_type = Counter(str(r.get("task_type", "?")) for r in recent)
    by_status = Counter(str(r.get("status", "?")) for r in recent)

    lines = [f"## 최근 에피소드 — 총 {len(recent)}개 (집계·메타만, 본문 비공개)", ""]
    lines.append("### task_type별")
    for t in sorted(by_type):
        lines.append(f"- {t}: {by_type[t]}")
    lines.append("")
    lines.append("### status별")
    for s in sorted(by_status):
        lines.append(f"- {s}: {by_status[s]}")
    lines.append("")
    lines.append("### 최근 활동 (timestamp · task_type · status)")
    for r in recent[:RECENT_BRIEF_N]:
        ts = str(r.get("timestamp", ""))
        lines.append(f"- {ts} · {r.get('task_type', '?')} · {r.get('status', '?')}")
    return lines + [""]


def _section_top_reused(pages: list[_PageInfo], express_idx: dict,
                        episode_idx: dict) -> list[str]:
    reused = []
    for p in pages:
        er = int(express_idx.get(p.slug, 0))
        ep = int(episode_idx.get(p.slug, 0))
        total = er + ep
        if total > 0:
            reused.append((p.slug, er, ep, total))
    reused.sort(key=lambda x: (-x[3], x[0]))
    top = reused[:TOP_REUSED_N]
    lines = [f"## Top 재사용 페이지 — {len(top)}개", ""]
    for slug, er, ep, total in top:
        lines.append(f"- {slug} — 재사용 {total} (express {er}, episode {ep})")
    return lines + [""]


def _section_low_confidence(pages: list[_PageInfo]) -> list[str]:
    low = [(p.slug, p.confidence) for p in pages
           if p.confidence is not None and p.confidence < LOW_CONFIDENCE_THRESHOLD]
    low.sort(key=lambda x: (x[1], x[0]))
    lines = [f"## 저신뢰 페이지 (confidence < {LOW_CONFIDENCE_THRESHOLD}) — {len(low)}개", ""]
    for slug, conf in low:
        lines.append(f"- {slug} — confidence {conf}")
    return lines + [""]


def _section_archive_candidates(pages: list[_PageInfo], inbound: dict, graph_index: dict,
                                express_idx: dict, episode_idx: dict,
                                now: datetime) -> list[str]:
    """archive 후보 = inbound 0 AND age>180일. memory_score 로 보존 가치 주석(낮을수록 우선)."""
    cands = []
    for p in pages:
        if inbound.get(p.slug):
            continue
        age = _age_days(p.fm, p.path, now)
        if age <= ARCHIVE_AGE_DAYS:
            continue
        entry = {
            "slug": p.slug,
            "access_count": p.fm.get("access_count", 0) if isinstance(p.fm, dict) else 0,
            "age_days": age,
            "express_reuse": express_idx.get(p.slug, 0),
            "episode_ref": episode_idx.get(p.slug, 0),
        }
        score = curate.compute_memory_score(entry, graph_index, p.fm, now=now)
        cands.append((p.slug, age, score))
    cands.sort(key=lambda x: (x[2], -x[1], x[0]))  # score 오름차순(낮을수록 archive 우선)
    lines = [f"## Archive 후보 (inbound 0 · age>{ARCHIVE_AGE_DAYS}일) — {len(cands)}개", ""]
    lines.append("> memory_score 낮을수록 재사용 가치 낮음(archive 우선). 실제 이동은 사람 결정.")
    for slug, age, score in cands:
        lines.append(f"- {slug} — {age}일, score={score:.1f}")
    return lines + [""]


def generate_report(
    wiki_root: Path,
    *,
    episodes_dir: Path | None = None,
    procedures_dir: Path | None = None,
    express_dir: Path | None = None,
    now: datetime | None = None,
) -> str:
    """집계 전용 markdown 리포트 텍스트 생성 (읽기 전용, verbatim episode 본문 금지).

    wiki_root: wiki 페이지 디렉토리(graph.json·메타파일 포함). 리포트도 이 직속에 쓰인다.
    episodes_dir/procedures_dir: wiki/ 밖 원장·절차 디렉토리(주입 가능).
    express_dir: 재사용 신호 스캔용 express 산출물 디렉토리(기본 wiki_root.parent/express).
    now: 날짜 기반 섹션(stale·archive·recency)의 결정성용 주입(기본 datetime.now()).
    """
    wiki_root = Path(wiki_root)
    episodes_dir = Path(episodes_dir) if episodes_dir is not None else DEFAULT_EPISODES_DIR
    procedures_dir = Path(procedures_dir) if procedures_dir is not None else DEFAULT_PROCEDURES_DIR
    express_dir = Path(express_dir) if express_dir is not None else wiki_root.parent / "express"
    if now is None:
        now = datetime.now()

    pages, parse_errors = _collect_pages(wiki_root)
    _, inbound = curate.build_link_graph([p.path for p in pages])
    express_idx = curate.build_express_reuse_index(express_dir)
    episode_idx = curate.build_episode_ref_index(episodes_dir)
    graph_index = curate.load_graph_index(wiki_root / "graph.json")

    lines = [
        f"# Memory Health Report — {now:%Y-%m-%d %H:%M}",
        "",
        "> 읽기 전용 집계 리포트(메타 기억 관측). 어떤 wiki 페이지도 이동·삭제·생성하지 않는다.",
        "> verbatim episode 본문 없음(§D 프라이버시). okf META_FILES 제외 — 공개 번들 미포함.",
        "",
    ]
    lines += _section_memory_types(pages)
    lines += _section_orphans(pages, inbound)
    lines += _section_stale_procedures(procedures_dir, now)
    lines += _section_recent_episodes(episodes_dir)
    lines += _section_top_reused(pages, express_idx, episode_idx)
    lines += _section_low_confidence(pages)
    lines += _section_archive_candidates(
        pages, inbound, graph_index, express_idx, episode_idx, now)

    if parse_errors:
        lines.append(f"## frontmatter 파싱 경고 — {len(parse_errors)}개")
        lines.append("")
        for rel, reason in parse_errors:
            lines.append(f"- `{rel}` — {reason}")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def write_report(
    wiki_root: Path,
    *,
    episodes_dir: Path | None = None,
    procedures_dir: Path | None = None,
    express_dir: Path | None = None,
    now: datetime | None = None,
) -> Path:
    """generate_report 결과를 wiki_root/memory_health_report.md 에 쓰고 경로 반환.

    유일한 부작용은 이 리포트 파일 쓰기뿐 — 다른 wiki 페이지는 절대 건드리지 않는다.
    """
    wiki_root = Path(wiki_root)
    text = generate_report(
        wiki_root, episodes_dir=episodes_dir, procedures_dir=procedures_dir,
        express_dir=express_dir, now=now,
    )
    report_path = wiki_root / REPORT_FILENAME
    report_path.write_text(text, encoding="utf-8")
    return report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="읽기전용 메모리 건강 리포트 → wiki/memory_health_report.md (US-008)"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="wiki/memory_health_report.md 생성(기본 동작)",
    )
    parser.parse_args(argv)  # --report 는 단일 동작이라 플래그 유무와 무관하게 리포트 생성

    if not DEFAULT_WIKI_ROOT.is_dir():
        print(f"[memory_health] ERROR: wiki dir not found: {DEFAULT_WIKI_ROOT}",
              file=sys.stderr)
        return 1
    path = write_report(DEFAULT_WIKI_ROOT)
    print(f"[memory_health] → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
