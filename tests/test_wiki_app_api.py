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


@pytest.mark.requires_user_wiki
def test_api_index_returns_metadata(client):
    r = client.get("/api/index")
    assert r.status_code == 200
    data = r.json()
    assert data["total_pages"] >= 40
    assert "categories" in data


@pytest.mark.requires_user_wiki
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


@pytest.mark.requires_user_wiki
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
# self-contained 엔드포인트 회귀 (tmp_path — 사용자 wiki 무의존)
# ---------------------------------------------------------------------------


def _build_project(tmp_path, *, with_index: bool, with_graph: bool):
    """tmp_path 안에 wiki_root + (옵션) index.md + (옵션) graph.json 구조.

    create_app/Index.build 가 wiki_root.parent/index.md 를 읽으므로 그 레이아웃 재현.
    반환: wiki_root Path.
    """
    project_root = tmp_path / "proj"
    wiki_root = project_root / "wiki"
    (wiki_root / "concepts").mkdir(parents=True)
    (wiki_root / "concepts" / "alpha.md").write_text(
        "---\ntitle: Alpha\ntags: [misc]\n---\n# Alpha\n\n본문.\n"
    )
    if with_index:
        (project_root / "index.md").write_text(
            "## concepts/ (1개)\n- [[alpha]] — 알파 페이지\n"
        )
    if with_graph:
        import json as _json
        (wiki_root / "graph.json").write_text(_json.dumps({
            "nodes": [{"id": "alpha", "kind": "page", "title": "Alpha",
                       "category": "concepts", "inbound": 0, "outbound": 0}],
            "links": [],
        }))
    return wiki_root


# --- 과제 1 회귀: index.md 부재가 create_app 부팅을 크래시시키지 않는다 ---
# WHY: Index.build 가 wiki_root.parent/index.md 를 무조건 읽어 부재 시
# FileNotFoundError 로 부팅이 죽었다. 부재 시 빈 인덱스로 graceful 부팅해야 한다.


def test_create_app_boots_without_index_md(tmp_path):
    wiki_root = _build_project(tmp_path, with_index=False, with_graph=False)

    # create_app 가 예외 없이 끝나야 한다 (부팅 크래시 금지).
    app = create_app(wiki_root=wiki_root)
    client = TestClient(app)

    r = client.get("/api/index")
    assert r.status_code == 200
    # index.md 가 없으면 slug 소스가 없어 0 페이지.
    assert r.json()["total_pages"] == 0


def test_search_endpoint_empty_index_returns_no_results(tmp_path):
    # index.md 부재 → 빈 인덱스 → 검색은 크래시 없이 빈 결과.
    wiki_root = _build_project(tmp_path, with_index=False, with_graph=False)
    client = TestClient(create_app(wiki_root=wiki_root))

    r = client.get("/api/search", params={"q": "alpha"})
    assert r.status_code == 200
    assert r.json()["total"] == 0


# --- 과제 2(a): /api/page/{slug}/graph 는 graph.json 부재 시 503 (현 분기 고정) ---
# WHY: api.py 는 graph.json 없으면 HTTPException(503) 를 던진다. 이 분기 동작을
# 회귀 테스트로 고정해, 의도치 않은 변경(예: 500 으로 떨어짐)을 잡는다.


def test_api_page_graph_returns_503_when_graph_json_missing(tmp_path):
    # graph.json 이 없는 wiki_root — graph 엔드포인트는 503 을 반환해야 한다.
    wiki_root = _build_project(tmp_path, with_index=True, with_graph=False)
    client = TestClient(create_app(wiki_root=wiki_root))

    r = client.get("/api/page/alpha/graph")
    assert r.status_code == 503


def test_api_page_graph_returns_neighborhood_when_graph_json_present(tmp_path):
    # 대비 경로: graph.json 이 있으면 503 이 아니라 center/neighbors/edges 를 준다.
    wiki_root = _build_project(tmp_path, with_index=True, with_graph=True)
    client = TestClient(create_app(wiki_root=wiki_root))

    r = client.get("/api/page/alpha/graph")
    assert r.status_code == 200
    data = r.json()
    assert data["center"]["slug"] == "alpha"
    assert "neighbors" in data
    assert "edges" in data


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


# ---------------------------------------------------------------------------
# stderr concurrent-drain regression test
#
# 잔여 결함(low): stream 엔드포인트가 stdout 을 EOF 까지 다 읽은 *뒤에야*
# stderr 를 읽으면, claude 가 stderr 를 많이 뱉을 때 stderr 파이프 버퍼가
# 차서 claude 가 stderr write 에서 블록 → stdout 진행도 멈춤 → stdout EOF 가
# 영원히 안 오는 이론적 데드락. fix = create_subprocess_exec 직후 stderr 를
# 백그라운드 task 로 동시 drain.
#
# 아래 fake proc 은 그 데드락을 충실히 모델링한다:
#   stdout 의 마지막 EOF 는 stderr.read() 가 *시작(await)* 된 뒤에만 도착한다.
#   - 동시 drain(수정 후): stderr drain task 가 즉시 시작 → EOF 도착 → 완료.
#   - 순차 read(수정 전): stdout EOF 를 먼저 기다림 → 영원히 hang → 테스트 timeout.
# ---------------------------------------------------------------------------


class _DrainGatedStdoutReader:
    """stdout reader: chunk 들을 흘려보낸 뒤, stderr drain 이 시작될 때까지
    EOF(b"")를 막아둔다. stderr 동시 drain 이 일어나야만 EOF 에 도달."""

    def __init__(self, lines: list[bytes], stderr_started: asyncio.Event):
        self._lines = list(lines)
        self._stderr_started = stderr_started

    async def readline(self) -> bytes:
        if self._lines:
            return self._lines.pop(0)
        # 모든 chunk 소진 → EOF 전에 stderr drain 시작을 기다림(데드락 재현)
        await self._stderr_started.wait()
        return b""


class _GatedStderrReader:
    """stderr reader: read() 가 호출(=drain 시작)되면 event 를 set 하고
    누적 stderr 내용을 반환. stdout EOF 게이트를 여는 역할."""

    def __init__(self, content: bytes, stderr_started: asyncio.Event):
        self._content = content
        self._stderr_started = stderr_started

    async def read(self) -> bytes:
        # drain 이 시작됐음을 알림 → stdout EOF 게이트 해제
        self._stderr_started.set()
        return self._content


class StderrDrainFakeProc:
    """stdout chunk 여러 개 + stderr 내용 보유, returncode≠0 인 fake proc.
    stderr 가 동시 drain 될 때만 stdout 이 EOF 에 도달하도록 게이팅."""

    def __init__(self, *, stdout_lines: list[bytes], stderr_content: bytes,
                 returncode: int):
        self._stderr_started = asyncio.Event()
        self.stdout = _DrainGatedStdoutReader(stdout_lines, self._stderr_started)
        self.stderr = _GatedStderrReader(stderr_content, self._stderr_started)
        self._returncode = returncode
        self.returncode = None
        self.killed = False
        self.waited = False

    def kill(self):
        self.killed = True

    async def wait(self):
        self.waited = True
        if self.returncode is None:
            self.returncode = self._returncode
        return self.returncode


def test_ai_answer_stream_drains_stderr_concurrently(client, patched_subprocess):
    """stream: claude 가 stderr 를 많이 뱉어도 stderr 를 stdout 과 동시 drain 해
    데드락 없이 완료해야 하고, returncode≠0 이면 stderr 메시지가 event: error 로
    표면화돼야 한다.

    fake proc 은 stderr.read() 가 시작돼야만 stdout 이 EOF 에 도달하도록 게이팅 —
    순차(EOF 후 stderr) 구현이면 이 테스트는 영원히 hang 한다. 따라서 hang 없이
    완료한다는 것 자체가 '동시 drain' 의 증거다.
    """
    err_msg = "claude: rate limit exceeded\n" * 50  # 큰 stderr (버퍼 채움 모사)
    proc = patched_subprocess(StderrDrainFakeProc(
        stdout_lines=[b"chunk-1\n", b"chunk-2\n", b"chunk-3\n"],
        stderr_content=err_msg.encode("utf-8"),
        returncode=1,
    ))

    with client.stream("POST", "/api/ai-answer/stream",
                       json={"question": "ping", "context_slugs": []}) as r:
        body = r.read().decode("utf-8")

    # (a) stderr 가 drain 돼 hang 없이 완료 — 모든 stdout chunk 가 표면화됨
    assert "chunk-1" in body
    assert "chunk-2" in body
    assert "chunk-3" in body
    # (b) non-zero returncode → stderr 메시지가 event: error 로 표면화
    assert "event: error" in body, "returncode≠0 시 event: error 방출해야 함"
    assert "rate limit exceeded" in body, "stderr 메시지가 error event 에 실려야 함"
    assert "event: done" not in body, "실패 케이스에선 done 이 아니라 error"
    # proc 은 정상 종료(returncode 설정) → finally 의 _terminate_proc 은 no-op
    assert proc.waited is True
