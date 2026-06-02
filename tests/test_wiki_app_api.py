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


# ---------------------------------------------------------------------------
# C3 — stream 무제한 수명 방어 (absolute deadline + chunk/byte cap)
#
# Codex [high]: readline 에 idle timeout 만 걸려 있으면 claude 가 deadline 안에
# 한 줄씩 계속 흘려보낼 때 전체 스트림이 무기한 지속된다. fix = (1) 스트림 전체에
# absolute deadline, (2) max chunks/bytes cap. 초과 시 event: error + proc 종료.
# 추가로 child 를 새 process group(start_new_session=True)으로 띄우고 cleanup 시
# process group 전체를 종료해 descendant 누수를 막는다.
# ---------------------------------------------------------------------------


class _InfiniteStdoutReader:
    """readline 이 매번 즉시 한 줄을 돌려준다 — 절대 EOF(b"")에 도달하지 않음.

    각 readline 은 빠르게 반환되므로 idle timeout 은 발동하지 않는다. 오직
    absolute deadline / chunk cap 만이 이 무한 스트림을 끊을 수 있다.
    """

    def __init__(self, line: bytes = b"tick\n"):
        self._line = line
        self.count = 0

    async def readline(self) -> bytes:
        self.count += 1
        return self._line

    async def read(self) -> bytes:
        return b""


class InfiniteFakeProc:
    """무한히 stdout 라인을 흘려보내는 fake proc. pid 보유(process-group 경로용)."""

    def __init__(self, line: bytes = b"tick\n"):
        self.stdout = _InfiniteStdoutReader(line=line)
        self.stderr = _FakeStreamReader(lines=[])
        self.returncode = None
        self.pid = 424242
        self.killed = False
        self.waited = False

    def kill(self):
        self.killed = True

    async def wait(self):
        self.waited = True
        if self.returncode is None:
            self.returncode = -9
        return self.returncode


def test_ai_answer_stream_absolute_deadline_terminates(client, patched_subprocess, monkeypatch):
    """stream: claude 가 deadline 안에 한 줄씩 계속 써도(idle timeout 미발동)
    전체 absolute deadline 을 넘기면 event: error + proc kill/wait 로 끊어야 한다."""
    proc = patched_subprocess(InfiniteFakeProc())

    # 실제 시계 대기 없이 deadline 초과를 강제: 시간이 deadline 보다 큰 폭으로
    # 흐르도록 monotonic 을 단조 증가 스텁으로 대체.
    fake_clock = {"t": 0.0}

    def fake_monotonic():
        fake_clock["t"] += 1000.0  # 한 번 호출될 때마다 1000초 경과 → 즉시 deadline 초과
        return fake_clock["t"]

    monkeypatch.setattr(api_module.time, "monotonic", fake_monotonic)

    with client.stream("POST", "/api/ai-answer/stream",
                       json={"question": "ping", "context_slugs": []}) as r:
        body = r.read().decode("utf-8")

    assert "event: error" in body, "deadline 초과 시 event: error 방출해야 함"
    assert proc.killed is True, "deadline 초과 시 proc.kill() 호출돼야 함"
    assert proc.waited is True, "deadline 초과 후 proc.wait() 가 await 돼야 함"
    # 무한 루프가 cap 으로 끊겼는지 — 유한 횟수만 읽었어야 한다(무기한 X)
    assert proc.stdout.count < 100000, "deadline 이 무한 스트림을 끊지 못함"


def test_ai_answer_stream_chunk_cap_terminates(client, patched_subprocess, monkeypatch):
    """stream: deadline 전이라도 chunk/byte cap 을 넘으면 event: error + 종료.

    시계는 진행시키지 않고(deadline 미발동) cap 을 작게 낮춰 chunk 수 초과만으로
    스트림이 끊기는지 검증한다."""
    proc = patched_subprocess(InfiniteFakeProc())

    # 시계는 고정 → deadline 절대 발동 안 함. cap 만으로 끊겨야 한다.
    monkeypatch.setattr(api_module.time, "monotonic", lambda: 0.0)
    monkeypatch.setattr(api_module, "_AI_STREAM_MAX_CHUNKS", 5)

    with client.stream("POST", "/api/ai-answer/stream",
                       json={"question": "ping", "context_slugs": []}) as r:
        body = r.read().decode("utf-8")

    assert "event: error" in body, "chunk cap 초과 시 event: error 방출해야 함"
    assert proc.killed is True, "chunk cap 초과 시 proc.kill() 호출돼야 함"
    assert proc.waited is True
    # cap 근방에서 끊겼는지 — 무한정 안 읽었어야 한다
    assert proc.stdout.count <= 100, "chunk cap 이 무한 스트림을 끊지 못함"


def test_stream_subprocess_started_in_new_session(client, patched_subprocess):
    """stream: create_subprocess_exec 호출이 start_new_session=True 로 child 를
    새 process group/session 에 띄워야 descendant 까지 process-group kill 가능."""
    proc = patched_subprocess(FakeProc(stdout_lines=[b"hi\n"]))
    captured = {}

    real_exec = api_module.asyncio.create_subprocess_exec  # patched_subprocess 가 이미 대체

    async def capturing_exec(*args, **kwargs):
        captured["kwargs"] = kwargs
        return await real_exec(*args, **kwargs)

    api_module.asyncio.create_subprocess_exec = capturing_exec
    try:
        with client.stream("POST", "/api/ai-answer/stream",
                           json={"question": "ping", "context_slugs": []}) as r:
            r.read()
    finally:
        api_module.asyncio.create_subprocess_exec = real_exec

    assert captured["kwargs"].get("start_new_session") is True, \
        "child 를 새 session(process group)으로 띄워야 함"


def test_terminate_proc_uses_process_group_kill(monkeypatch):
    """_terminate_proc 은 pid 가 있으면 os.killpg(os.getpgid(pid), SIGKILL) 로
    process group 전체를 종료해야 한다 (descendant 누수 방지)."""
    import os
    import signal

    calls = {"getpgid": None, "killpg": None}

    def fake_getpgid(pid):
        calls["getpgid"] = pid
        return pid  # pgid == pid (leader)

    def fake_killpg(pgid, sig):
        calls["killpg"] = (pgid, sig)

    monkeypatch.setattr(os, "getpgid", fake_getpgid)
    monkeypatch.setattr(os, "killpg", fake_killpg)

    proc = InfiniteFakeProc()  # pid=424242, returncode=None(살아있음)

    asyncio.run(api_module._terminate_proc(proc))

    assert calls["getpgid"] == 424242, "os.getpgid(pid) 가 호출돼야 함"
    assert calls["killpg"] == (424242, signal.SIGKILL), \
        "os.killpg(pgid, SIGKILL) 로 그룹 전체를 종료해야 함"
    assert proc.waited is True, "process-group kill 후에도 proc.wait() 가 await 돼야 함"


def test_terminate_proc_falls_back_to_kill_without_pgid(monkeypatch):
    """_terminate_proc 은 os.getpgid 가 실패(pid 없음 등)하면 graceful 하게
    proc.kill() 로 fallback 해야 한다 (테스트 fake proc / 플랫폼 호환)."""
    import os

    def boom_getpgid(pid):
        raise ProcessLookupError()

    monkeypatch.setattr(os, "getpgid", boom_getpgid)

    proc = FakeProc(communicate_hang=True)  # returncode=None, pid 없음

    asyncio.run(api_module._terminate_proc(proc))

    assert proc.killed is True, "process-group kill 실패 시 proc.kill() 로 fallback 해야 함"
    assert proc.waited is True


# ---------------------------------------------------------------------------
# C4 — AIAnswerRequest 입력 검증 (size / count / slug pattern)
#
# Codex [med]: question/context_slugs 길이·개수·패턴 무제한 → DoS 표면.
# fix = Pydantic Field 제약. 위반 시 FastAPI 가 자동 422.
# ---------------------------------------------------------------------------


def test_ai_answer_rejects_oversized_question(client):
    """question 이 max_length 를 넘으면 422 (Pydantic 검증)."""
    huge = "가" * 100_000
    r = client.post("/api/ai-answer", json={"question": huge, "context_slugs": []})
    assert r.status_code == 422


def test_ai_answer_rejects_too_many_context_slugs(client):
    """context_slugs 개수가 max_items 를 넘으면 422."""
    slugs = [f"slug-{i}" for i in range(100)]
    r = client.post("/api/ai-answer", json={"question": "ping", "context_slugs": slugs})
    assert r.status_code == 422


def test_ai_answer_rejects_path_traversal_slug(client):
    """slug 에 path traversal('..')/구분자('/') 가 들어가면 422."""
    for bad in ["../etc/passwd", "a/b", "..", "foo/../bar"]:
        r = client.post("/api/ai-answer",
                        json={"question": "ping", "context_slugs": [bad]})
        assert r.status_code == 422, f"악성 slug 거부 실패: {bad!r}"


def test_ai_answer_rejects_oversized_slug(client):
    """개별 slug 가 max_length 를 넘으면 422."""
    long_slug = "a" * 5000
    r = client.post("/api/ai-answer",
                    json={"question": "ping", "context_slugs": [long_slug]})
    assert r.status_code == 422


def test_ai_answer_accepts_valid_slug_pattern(client, patched_subprocess):
    """정상 slug(소문자-하이픈-숫자, 한글 포함)은 통과해야 한다 (회귀 방지).

    claude CLI 를 fake 로 대체해 검증 통과 후 정상 done 응답까지 확인.
    """
    patched_subprocess(FakeProc(communicate_hang=False))
    r = client.post("/api/ai-answer",
                    json={"question": "ping", "context_slugs": ["habix-profile", "개념-노트"]})
    assert r.status_code == 200
    assert r.json()["status"] == "done"
