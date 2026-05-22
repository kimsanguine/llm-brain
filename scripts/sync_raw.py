#!/usr/bin/env python3
"""
sync_raw.py — sources.yaml의 소스 경로에서 raw/ 폴더로 델타 미러링.
변경·신규 파일만 복사한다. raw/ 파일은 삭제하지 않는다.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml

WIKI_ROOT = Path(__file__).parent.parent
SOURCES_FILE = WIKI_ROOT / "schema" / "sources.yaml"
STATE_FILE = WIKI_ROOT / ".sync_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def should_exclude(file: Path, exclude_tags: list[str]) -> bool:
    if not exclude_tags:
        return False
    try:
        post = frontmatter.load(str(file))
        file_tags = post.metadata.get("tags", [])
        if isinstance(file_tags, str):
            file_tags = [file_tags]
        return bool(set(exclude_tags) & set(file_tags))
    except Exception:
        return False


def sync_source(source_cfg: dict, state: dict) -> tuple[int, int]:
    src = Path(source_cfg["source"]).expanduser()
    dst = WIKI_ROOT / source_cfg["target"]
    exclude_tags = source_cfg.get("exclude_tags", [])
    source_id = source_cfg["id"]

    if not src.exists():
        print(f"  [SKIP] 소스 없음: {src}")
        return 0, 0

    SUPPORTED = {".md", ".txt", ".pdf", ".docx", ".pptx"}
    extensions = {
        f".{e.lstrip('.')}" for e in source_cfg.get("extensions", [])
    } or SUPPORTED

    dst.mkdir(parents=True, exist_ok=True)
    last_sync = state.get(source_id, "1970-01-01T00:00:00")
    last_sync_dt = datetime.fromisoformat(last_sync)

    copied = skipped = 0
    for src_file in sorted(src.rglob("*")):
        if not src_file.is_file():
            continue
        if src_file.suffix.lower() not in extensions:
            skipped += 1
            continue
        if src_file.stat().st_mtime <= last_sync_dt.timestamp():
            skipped += 1
            continue
        if should_exclude(src_file, exclude_tags):
            skipped += 1
            continue

        rel = src_file.relative_to(src)
        dst_file = dst / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied += 1

    state[source_id] = datetime.now().isoformat()
    return copied, skipped


def sync_git_repo(repo_cfg: dict) -> tuple[int, int]:
    """git 레포를 로컬에 clone/pull 후 raw/로 복사."""
    import subprocess

    repo_url = repo_cfg["url"]
    repo_id = repo_cfg["id"]
    local_path = Path(repo_cfg.get("local_path", f"~/.llm-brain-cache/{repo_id}")).expanduser()

    # clone 또는 pull
    if local_path.exists():
        result = subprocess.run(
            ["git", "-C", str(local_path), "pull", "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [{repo_id}] git pull 실패: {result.stderr.strip()}")
            return 0, 0
    else:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--quiet", repo_url, str(local_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [{repo_id}] git clone 실패: {result.stderr.strip()}")
            return 0, 0

    # clone된 raw/ → 로컬 raw/ 복사
    src_raw = local_path / "raw"
    if not src_raw.exists():
        return 0, 0

    copied = skipped = 0
    SUPPORTED = {".md", ".txt", ".pdf", ".docx", ".pptx"}
    for src_file in sorted(src_raw.rglob("*")):
        if not src_file.is_file():
            continue
        if src_file.name == ".gitkeep":
            skipped += 1
            continue
        if src_file.suffix.lower() not in SUPPORTED:
            skipped += 1
            continue
        rel = src_file.relative_to(local_path / "raw")
        dst_file = WIKI_ROOT / "raw" / rel
        if dst_file.exists() and dst_file.stat().st_mtime >= src_file.stat().st_mtime:
            skipped += 1
            continue
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied += 1

    return copied, skipped


def main() -> None:
    config = yaml.safe_load(SOURCES_FILE.read_text())
    state = load_state()

    print(f"[sync_raw] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    total_copied = 0

    # 일반 로컬 소스 동기화
    for source in config.get("sources", []):
        if source.get("disabled"):
            continue
        copied, skipped = sync_source(source, state)
        print(f"  [{source['id']}] 복사 {copied}개, 건너뜀 {skipped}개")
        total_copied += copied

    # git 레포 소스 동기화 (llm-brain-private 등)
    for repo in config.get("git_repos", []):
        if repo.get("disabled"):
            continue
        copied, skipped = sync_git_repo(repo)
        print(f"  [{repo['id']}] git 복사 {copied}개, 건너뜀 {skipped}개")
        total_copied += copied

    save_state(state)
    print(f"[sync_raw] 완료 — 총 {total_copied}개 파일 복사")

    if total_copied == 0 and "--quiet" not in sys.argv:
        print("[sync_raw] 새 파일 없음. ingest 불필요.")
        sys.exit(0)


if __name__ == "__main__":
    main()
