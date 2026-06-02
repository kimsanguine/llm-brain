import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

import wiki_app.api as api_module
from wiki_app.api import create_app


WIKI_ROOT = Path(__file__).parent.parent / "wiki"


@pytest.fixture(scope="module")
def client():
    app = create_app(wiki_root=WIKI_ROOT)
    return TestClient(app)


def test_api_index_returns_metadata(client):
    r = client.get("/api/index")
    assert r.status_code == 200
    data = r.json()
    assert data["total_pages"] >= 40
    assert "categories" in data


def test_api_search_returns_results(client):
    r = client.get("/api/search", params={"q": "habix"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "habix"
    assert data["total"] > 0
    slugs = [r["slug"] for r in data["results"]]
    assert "habix-profile" in slugs


def test_api_search_empty_query(client):
    r = client.get("/api/search", params={"q": ""})
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_api_page_returns_html_and_metadata(client):
    r = client.get("/api/page/habix-profile")
    assert r.status_code == 200
    data = r.json()
    assert data["slug"] == "habix-profile"
    assert "<h1>" in data["html"]
    assert "frontmatter" in data
    assert "inbound" in data
    assert "outbound" in data


def test_api_page_unknown_slug_404(client):
    r = client.get("/api/page/nonexistent-xyz")
    assert r.status_code == 404


def test_api_ai_answer_contract(client):
    """AI endpoint의 응답 contract만 검증 (실제 LLM 응답은 환경별).

    Local (claude CLI 있음) → status=done + answer 비어있지 않음 (10-30s)
    CI    (claude CLI 없음) → status=unavailable (즉시)
    """
    r = client.post("/api/ai-answer", json={
        "question": "ping",
        "context_slugs": [],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("done", "unavailable", "timeout", "error")
    assert "answer" in data
    assert "sources" in data
    assert data["question"] == "ping"


# ---------------------------------------------------------------------------
# subprocess lifecycle regression tests
#
# Codex [high]: claude -p subprocess가 timeout/disconnect/stream error 시
# kill()+wait() 되지 않아 좀비/누적이 발생. 아래 테스트는 fake proc 으로
# create_subprocess_exec 를 대체해 "endpoint 가 timeout/오류 경로를 탔을 때
# proc.kill() 이 호출되고 proc.wait() 가 await 되는지"를 검증한다.
# ---------------------------------------------------------------------------


class _FakeStreamReader:
    """asyncio.StreamReader 흉내 — readline 이 영원히 hang(스트림 hang 재현)."""

    def __init__(self, hang: bool = False, lines: list[bytes] | None = None):
        self._hang = hang
        self._lines = list(lines or [])

    async def readline(self) -> bytes:
        if self._hang:
            # claude hang 재현 — 깨어나지 않는 future 를 대기
            await asyncio.Future()
        if self._lines:
            return self._lines.pop(0)
        return b""

    async def read(self) -> bytes:
        return b""


class FakeProc:
    """asyncio subprocess 흉내. kill()/wait() 호출을 플래그로 추적."""

    def __init__(self, *, communicate_hang: bool = False, stdout_hang: bool = False,
                 stdout_lines: list[bytes] | None = None, returncode_after_wait: int = 0):
        self.stdout = _FakeStreamReader(hang=stdout_hang, lines=stdout_lines)
        self.stderr = _FakeStreamReader(lines=[])
        self._communicate_hang = communicate_hang
        self._returncode_after_wait = returncode_after_wait
        self.returncode = None
        self.killed = False
        self.waited = False

    async def communicate(self):
        if self._communicate_hang:
            await asyncio.Future()  # 영원히 hang → wait_for timeout 유발
        self.returncode = 0
        return (b"answer text", b"")

    def kill(self):
        self.killed = True

    async def wait(self):
        self.waited = True
        # kill 후 returncode 확정 (실제 proc 의미)
        if self.returncode is None:
            self.returncode = self._returncode_after_wait
        return self.returncode


@pytest.fixture
def patched_subprocess(monkeypatch):
    """shutil.which("claude") 가 존재하게 하고, create_subprocess_exec 를
    호출자가 주입한 FakeProc 으로 대체하는 헬퍼.

    반환: install(proc) — 해당 proc 을 사용하도록 패치하고 그 proc 을 돌려줌.
    """

    def install(proc: FakeProc) -> FakeProc:
        monkeypatch.setattr(api_module.shutil, "which", lambda name: "/usr/bin/claude")

        async def fake_exec(*args, **kwargs):
            return proc

        monkeypatch.setattr(api_module.asyncio, "create_subprocess_exec", fake_exec)
        return proc

    return install


def test_ai_answer_timeout_kills_and_waits_subprocess(client, patched_subprocess, monkeypatch):
    """non-stream: communicate() 가 timeout 되면 endpoint 는 status=timeout 을
    반환하면서 child 를 kill() + wait() 해야 한다 (좀비 방지)."""
    proc = patched_subprocess(FakeProc(communicate_hang=True))

    # 90초 실제 대기 대신 wait_for 가 즉시 TimeoutError 를 던지게 함
    async def fast_wait_for(aw, timeout):
        # endpoint 의 communicate() 대기를 즉시 timeout 처리.
        # 넘겨받은 coroutine 은 닫아 RuntimeWarning 방지.
        if asyncio.iscoroutine(aw):
            aw.close()
        raise asyncio.TimeoutError()

    monkeypatch.setattr(api_module.asyncio, "wait_for", fast_wait_for)

    r = client.post("/api/ai-answer", json={"question": "ping", "context_slugs": []})
    assert r.status_code == 200
    assert r.json()["status"] == "timeout"

    # 핵심 단언: timeout 시 proc 정리
    assert proc.killed is True, "timeout 시 proc.kill() 이 호출되어야 함"
    assert proc.waited is True, "kill 후 proc.wait() 가 await 되어야 함"


def test_ai_answer_normal_does_not_leave_running_proc(client, patched_subprocess):
    """non-stream 정상 경로: 정상 종료한 proc 은 done 을 반환하고,
    이미 종료된 proc 에 대해 추가 kill 로 깨지지 않아야 한다."""
    proc = patched_subprocess(FakeProc(communicate_hang=False))

    r = client.post("/api/ai-answer", json={"question": "ping", "context_slugs": []})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "done"
    assert data["answer"] == "answer text"
    # 정상 종료(returncode 설정됨) → 살아있지 않으므로 강제 kill 불필요
    assert proc.killed is False


def test_ai_answer_stream_hang_kills_and_waits_subprocess(client, patched_subprocess, monkeypatch):
    """stream: readline() 이 영원히 hang 하면 idle/전체 timeout 후 proc 을
    kill() + wait() 하고 event: error 를 방출해야 한다."""
    proc = patched_subprocess(FakeProc(stdout_hang=True))

    real_wait_for = asyncio.wait_for

    async def fast_wait_for(aw, timeout):
        # stream readline 대기를 즉시 timeout 처리. 그 외 wait() 같은
        # 코루틴은 정상 대기시켜 정리 로직이 실제로 await 되게 함.
        if asyncio.iscoroutine(aw):
            # readline 코루틴만 timeout, 나머지는 실제 await
            name = getattr(getattr(aw, "cr_code", None), "co_name", "")
            if name == "readline":
                aw.close()
                raise asyncio.TimeoutError()
            return await real_wait_for(aw, timeout)
        return await real_wait_for(aw, timeout)

    monkeypatch.setattr(api_module.asyncio, "wait_for", fast_wait_for)

    with client.stream("POST", "/api/ai-answer/stream",
                       json={"question": "ping", "context_slugs": []}) as r:
        body = r.read().decode("utf-8")

    # 핵심 단언: stream hang 시 proc 정리
    assert proc.killed is True, "stream timeout 시 proc.kill() 이 호출되어야 함"
    assert proc.waited is True, "stream timeout 후 proc.wait() 가 await 되어야 함"
    assert "event: error" in body, "hang 시 event: error 를 방출해야 함"
