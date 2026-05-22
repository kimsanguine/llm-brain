import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import frontmatter

from wiki_app.access import track


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


def test_track_increments_access_count(tmp_path, monkeypatch):
    # wiki 폴더를 복사한 임시 위치에서 테스트 (실제 wiki를 오염시키지 않기 위해)
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)

    test_page = test_wiki / "business" / "habix-profile.md"
    before = frontmatter.load(test_page).metadata.get("access_count", 0)

    track("habix-profile", wiki_root=test_wiki)

    after = frontmatter.load(test_page).metadata.get("access_count", 0)
    assert after == before + 1


def test_track_unknown_slug_does_not_raise(tmp_path, monkeypatch):
    import shutil
    test_wiki = tmp_path / "wiki"
    shutil.copytree(WIKI_ROOT, test_wiki)
    monkeypatch.chdir(tmp_path)
    # 알 수 없는 slug — 조용히 skip (예외 X)
    track("nonexistent-slug-xyz", wiki_root=test_wiki)
