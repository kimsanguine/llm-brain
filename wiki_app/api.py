"""FastAPI app — 6 endpoints + static mount."""
from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
import re
import shutil
import signal
import time
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AfterValidator, BaseModel, Field

from wiki_app import access, pages, render, search


# 한 segment 내부 허용 문자: 한글/영문/숫자/하이픈/언더스코어만.
# (segment = slug 를 '/' 로 나눈 각 조각)
_SEGMENT_PATTERN = re.compile(r"^[\w가-힣-]+$")


def _validate_slug(slug: str) -> str:
    """slug 안전성을 segment 단위로 검증한다.

    `pages.find_page_path` 의 containment 모델("wiki_root 내부의 중첩 slug 는 허용,
    밖으로 나가는 traversal 은 거부")에 맞춰, '/' 전면 금지 대신 segment 단위로
    위험 요소만 거른다:

    - 절대경로(선행 '/'), 백슬래시('\\') 금지 (path 주입 차단)
    - 빈 segment('a//b', 'a/', '/a') 금지
    - '..' segment 금지 (traversal 차단)
    - 그 외 segment 는 단어 문자/한글/하이픈만 허용

    이를 통과한 '/' 포함 중첩 slug("260515_llm_wiki/prd" 등)는 허용되며,
    실제 wiki_root 내부 존재 여부는 `_collect_context` 의 containment 가
    최종 게이트로 처리한다(통과 못 하면 조용히 제외).

    위반 시 ValueError → FastAPI 가 422 로 변환한다.
    """
    if slug.startswith("/") or "\\" in slug:
        raise ValueError(f"invalid slug (절대경로/백슬래시 금지): {slug!r}")
    segments = slug.split("/")
    for seg in segments:
        if seg == "" or seg == "..":
            raise ValueError(f"invalid slug (빈 segment/traversal 금지): {slug!r}")
        if not _SEGMENT_PATTERN.match(seg):
            raise ValueError(f"invalid slug segment: {seg!r}")
    return slug


# 개별 slug 제약: 길이 cap + segment 단위 안전성 검증.
_Slug = Annotated[
    str,
    Field(min_length=1, max_length=128),
    AfterValidator(_validate_slug),
]


class AIAnswerRequest(BaseModel):
    """AI 답변 요청 — 입력 크기/개수/패턴 제약으로 DoS 표면 축소.

    위반 시 FastAPI 가 자동으로 422 를 반환한다.
    """

    question: str = Field(min_length=1, max_length=4000)
    context_slugs: list[_Slug] = Field(default_factory=list, max_length=20)


# claude -p subprocess timeout (초)
_AI_ANSWER_TIMEOUT = 90
# stream: 한 줄 사이 idle timeout (초) — claude hang 방지
_AI_STREAM_IDLE_TIMEOUT = 90
# stream: 전체 absolute deadline (초) — claude 가 한 줄씩 계속 써도 무기한 방지
_AI_STREAM_DEADLINE = 180
# stream: 누적 chunk/byte 상한 — 폭주 출력 방지
_AI_STREAM_MAX_CHUNKS = 5000
_AI_STREAM_MAX_BYTES = 4_000_000
# context 페이지 본문 char cap — prompt 비용/토큰 폭주 방지 (페이지당 잘라 넣음)
_AI_CONTEXT_BODY_CHARS = 8000


def _collect_context(slugs, wiki_root):
    """context_slugs → (context 문자열, 유효 slug 목록). 페이지 본문은 char cap.

    non-stream/stream 양쪽이 동일 로직을 쓰도록 추출.
    """
    chunks = []
    valid = []
    for slug in slugs[:5]:  # 최대 5개 (토큰 제어)
        try:
            page = pages.load_page(slug, wiki_root=wiki_root)
        except pages.PageNotFound:
            continue
        body = page["body_md"][:_AI_CONTEXT_BODY_CHARS]
        chunks.append(f"## {slug}\n\n{body}")
        valid.append(slug)
    context = "\n\n---\n\n".join(chunks) if chunks else "(컨텍스트 페이지 없음)"
    return context, valid


async def _terminate_proc(proc) -> None:
    """proc(+descendant) 이 살아있으면 종료 후 wait — 좀비/누적/누수 방지.

    timeout·error·disconnect·정상 종료 어디서 호출돼도 안전(idempotent):
    이미 종료된 proc(returncode 설정됨)은 건드리지 않는다.

    child 를 start_new_session=True 로 띄웠으므로 child 는 자기 process group 의
    leader 다. os.killpg 로 group 전체를 SIGKILL 해 claude 가 spawn 한 descendant
    까지 정리한다. pid 부재/플랫폼 비호환 등으로 group kill 이 실패하면 graceful
    하게 proc.kill() 로 fallback 한다.
    """
    if proc is None:
        return
    if proc.returncode is None:
        if not _kill_process_group(proc):
            try:
                proc.kill()
            except ProcessLookupError:
                # 이미 사라진 child — 무시
                pass
        # wait 자체도 무한 대기하지 않도록 timeout (SIGKILL 후 회수는 즉시여야 정상).
        # asyncio.timeout() 사용 — endpoint 가 wait_for 를 monkeypatch 해도 영향 X.
        try:
            async with asyncio.timeout(10):
                await proc.wait()
        except (asyncio.TimeoutError, ProcessLookupError):
            pass


def _kill_process_group(proc) -> bool:
    """proc 의 process group 전체를 SIGKILL. 성공 시 True.

    pid 없음(fake proc)·getpgid/killpg 실패 시 False 를 돌려 호출자가
    proc.kill() 로 fallback 하게 한다.
    """
    pid = getattr(proc, "pid", None)
    if pid is None:
        return False
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
        return True
    except (ProcessLookupError, PermissionError, OSError, AttributeError):
        return False


def create_app(wiki_root: Path | None = None) -> FastAPI:
    """앱 팩토리 — wiki_root 인자로 test 격리 가능."""
    if wiki_root is None:
        wiki_root = Path(__file__).resolve().parent.parent / "wiki"

    app = FastAPI(title="LLM Wiki", version="0.1.0")
    index = search.Index.build(wiki_root=wiki_root)
    built_at = _dt.datetime.now(_dt.timezone.utc).isoformat()

    @app.get("/api/index")
    def api_index():
        cats = sorted({e.category for e in index.by_slug.values()})
        return {
            "total_pages": index.total_pages,
            "total_links": _count_links(wiki_root),
            "categories": cats,
            "last_built": built_at,
        }

    @app.get("/api/search")
    def api_search(q: str = ""):
        return index.search(q)

    @app.get("/api/page/{slug:path}/graph")
    def api_page_graph(slug: str):
        """페이지의 1-depth neighborhood graph (mini-graph 용).

        응답: {
          "center": {slug, title, category, degree},
          "neighbors": [{slug, title, category, direction: "in"|"out"|"both"}],
          "edges": [{source, target}]
        }
        """
        import json as _json

        graph_path = wiki_root / "graph.json"
        if not graph_path.exists():
            raise HTTPException(status_code=503, detail="graph.json 없음 — export_graph 먼저")
        g = _json.loads(graph_path.read_text())
        pages_map = {n["id"]: n for n in g["nodes"] if n["kind"] == "page"}
        if slug not in pages_map:
            raise HTTPException(status_code=404, detail=f"page not found: {slug}")

        center = pages_map[slug]
        wikilinks = [l for l in g["links"] if l["kind"] == "wikilink"]

        # 1-depth in/out 이웃
        out_targets = {l["target"] for l in wikilinks if l["source"] == slug and l["target"] in pages_map}
        in_sources = {l["source"] for l in wikilinks if l["target"] == slug and l["source"] in pages_map}
        both = out_targets & in_sources
        only_out = out_targets - in_sources
        only_in = in_sources - out_targets

        neighbors = []
        for s in sorted(both):
            neighbors.append({"slug": s, "title": pages_map[s].get("title", s),
                              "category": pages_map[s]["category"], "direction": "both"})
        for s in sorted(only_out):
            neighbors.append({"slug": s, "title": pages_map[s].get("title", s),
                              "category": pages_map[s]["category"], "direction": "out"})
        for s in sorted(only_in):
            neighbors.append({"slug": s, "title": pages_map[s].get("title", s),
                              "category": pages_map[s]["category"], "direction": "in"})

        # edges: center↔neighbor만 (depth 1)
        related_slugs = {slug} | out_targets | in_sources
        edges = [
            {"source": l["source"], "target": l["target"]}
            for l in wikilinks
            if l["source"] in related_slugs and l["target"] in related_slugs
        ]

        return {
            "center": {
                "slug": slug,
                "title": center.get("title", slug),
                "category": center["category"],
                "degree": len(out_targets | in_sources),
            },
            "neighbors": neighbors,
            "edges": edges,
        }

    @app.get("/api/page/{slug:path}")
    def api_page(slug: str):
        try:
            page = pages.load_page(slug, wiki_root=wiki_root)
        except pages.PageNotFound:
            raise HTTPException(status_code=404, detail=f"page not found: {slug}")
        # access_count 갱신 (조용히 실패)
        try:
            access.track(slug, wiki_root=wiki_root)
        except Exception:
            pass
        return {
            "slug": page["slug"],
            "title": page["frontmatter"].get("title", slug),
            "category": page["category"],
            "frontmatter": _sanitize_frontmatter(page["frontmatter"]),
            "html": render.render_markdown(page["body_md"]),
            "inbound": page["inbound"],
            "outbound": page["outbound"],
        }

    @app.post("/api/ai-answer")
    async def api_ai_answer(req: AIAnswerRequest):
        """`claude -p` CLI를 호출해 wiki 페이지 컨텍스트 기반으로 답변 생성.

        context_slugs 비어있으면 결과 없음 시나리오 → 사용자 질문만 그대로 전달.
        """
        # CLI 부재 시 graceful fallback
        if shutil.which("claude") is None:
            return {
                "status": "unavailable",
                "message": "Claude Code CLI를 찾을 수 없습니다. `claude` 명령을 PATH에 추가해주세요.",
                "question": req.question,
                "context_slugs": req.context_slugs,
                "answer": "",
                "sources": [],
            }

        # 컨텍스트 페이지 본문 수집 (페이지당 char cap)
        context, valid_slugs = _collect_context(req.context_slugs, wiki_root)
        prompt = (
            "다음 wiki 페이지 컨텍스트만 사용해 사용자 질문에 답변해주세요. "
            "컨텍스트에 없는 사실은 추측하지 말고 '관련 정보 없음'으로 답하세요.\n\n"
            f"# 사용자 질문\n{req.question}\n\n"
            f"# 컨텍스트\n{context}"
        )

        proc = None
        try:
            # start_new_session=True: child 를 새 process group/session 의 leader 로
            # 띄워 cleanup 시 process group 전체(descendant 포함)를 종료할 수 있게 한다.
            proc = await asyncio.create_subprocess_exec(
                "claude", "-p", prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
            )
            # 90초 timeout (큰 컨텍스트 + 추론 여유)
            stdout, _stderr = await asyncio.wait_for(
                proc.communicate(), timeout=_AI_ANSWER_TIMEOUT
            )
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "message": f"AI 답변 생성이 {_AI_ANSWER_TIMEOUT}초를 초과해 중단됐어요.",
                "question": req.question,
                "context_slugs": valid_slugs,
                "answer": "",
                "sources": valid_slugs,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"claude CLI 호출 중 오류: {type(e).__name__}",
                "question": req.question,
                "context_slugs": valid_slugs,
                "answer": "",
                "sources": [],
            }
        finally:
            # timeout·error·정상 어디서든 살아있는 child 는 반드시 정리
            await _terminate_proc(proc)

        answer = stdout.decode("utf-8", errors="replace").strip()
        return {
            "status": "done",
            "message": "",
            "question": req.question,
            "context_slugs": valid_slugs,
            "answer": answer,
            "sources": valid_slugs,
        }

    @app.post("/api/ai-answer/stream")
    async def api_ai_answer_stream(req: AIAnswerRequest):
        """SSE streaming version of /api/ai-answer.

        Event types:
          - meta:   {context_slugs}    # 한 번
          - chunk:  {text}              # 여러 번 (claude stdout 라인 단위)
          - done:   {}                  # 마지막
          - error:  {message}           # 실패 시
        """
        import json as _json

        async def event_gen():
            if shutil.which("claude") is None:
                yield f"event: error\ndata: {_json.dumps({'message': 'Claude Code CLI 없음'}, ensure_ascii=False)}\n\n"
                return

            # context 수집 (non-stream 과 동일 로직 · 페이지당 char cap)
            context, valid_slugs = _collect_context(req.context_slugs, wiki_root)

            yield f"event: meta\ndata: {_json.dumps({'context_slugs': valid_slugs}, ensure_ascii=False)}\n\n"

            prompt = (
                "다음 wiki 페이지 컨텍스트만 사용해 사용자 질문에 답변해주세요. "
                "컨텍스트에 없는 사실은 추측하지 말고 '관련 정보 없음'으로 답하세요.\n\n"
                f"# 사용자 질문\n{req.question}\n\n"
                f"# 컨텍스트\n{context}"
            )

            proc = None
            stderr_task = None
            try:
                # start_new_session=True: process group leader 로 띄워 cleanup 시
                # group 전체(claude 가 spawn 한 descendant 포함) 종료 가능.
                proc = await asyncio.create_subprocess_exec(
                    "claude", "-p", prompt,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    start_new_session=True,
                )
                # stderr 를 stdout 과 *동시* drain — claude 가 stderr 를 많이
                # 뱉을 때 stderr 파이프 버퍼가 차서 claude 가 막히고 stdout 진행이
                # 멈추는 데드락 방지 (잔여1). EOF 까지 백그라운드 수집.
                assert proc.stderr is not None
                stderr_task = asyncio.create_task(proc.stderr.read())
                # stdout을 라인 단위로 streaming
                assert proc.stdout is not None
                # idle timeout(줄 사이 hang) 외에 *전체* absolute deadline +
                # 누적 chunk/byte cap 으로 무기한 스트림(한 줄씩 영원히 흘림)도 끊는다.
                deadline = time.monotonic() + _AI_STREAM_DEADLINE
                chunk_count = 0
                byte_count = 0
                terminated_early = False  # deadline/cap 으로 끊었는지 (정상 EOF 와 구분)
                while True:
                    if time.monotonic() >= deadline:
                        yield f"event: error\ndata: {_json.dumps({'message': f'AI 답변이 {_AI_STREAM_DEADLINE}초 제한을 초과해 중단됐어요.'}, ensure_ascii=False)}\n\n"
                        terminated_early = True
                        break
                    if chunk_count >= _AI_STREAM_MAX_CHUNKS or byte_count >= _AI_STREAM_MAX_BYTES:
                        yield f"event: error\ndata: {_json.dumps({'message': 'AI 답변 출력 한도를 초과해 중단됐어요.'}, ensure_ascii=False)}\n\n"
                        terminated_early = True
                        break
                    # readline 에 idle timeout — claude hang 시 영원히 대기 방지
                    line = await asyncio.wait_for(
                        proc.stdout.readline(), timeout=_AI_STREAM_IDLE_TIMEOUT
                    )
                    if not line:
                        break
                    chunk_count += 1
                    byte_count += len(line)
                    text = line.decode("utf-8", errors="replace")
                    yield f"event: chunk\ndata: {_json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                if terminated_early:
                    # deadline/cap 으로 끊음 → error 이미 방출. child(+descendant)
                    # 즉시 정리해 무한 출력 proc 가 계속 돌지 않게 한다.
                    # (finally 도 정리하지만 여기서 조기 종료해 누수 시간 최소화)
                    await _terminate_proc(proc)
                else:
                    # stdout EOF — 종료 대기 후 동시 drain 한 stderr 회수
                    await proc.wait()
                    stderr_bytes = await stderr_task
                    if proc.returncode not in (0, None):
                        msg = stderr_bytes.decode("utf-8", errors="replace").strip() \
                            or f"claude exited with code {proc.returncode}"
                        yield f"event: error\ndata: {_json.dumps({'message': msg}, ensure_ascii=False)}\n\n"
                    else:
                        yield "event: done\ndata: {}\n\n"
            except asyncio.TimeoutError:
                yield f"event: error\ndata: {_json.dumps({'message': 'AI 답변 생성이 지연돼 중단됐어요.'}, ensure_ascii=False)}\n\n"
            except asyncio.CancelledError:
                # 클라이언트 disconnect — proc 정리 후 전파
                await _terminate_proc(proc)
                raise
            except Exception as e:
                yield f"event: error\ndata: {_json.dumps({'message': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"
            finally:
                # timeout·error·정상·disconnect 어디서든 살아있는 child 정리
                await _terminate_proc(proc)
                # 동시 drain task 가 아직 살아있으면(비정상 경로) 취소·회수 — leak 방지
                if stderr_task is not None and not stderr_task.done():
                    stderr_task.cancel()
                    try:
                        await stderr_task
                    except (asyncio.CancelledError, Exception):
                        pass

        return StreamingResponse(event_gen(), media_type="text/event-stream")

    # 정적 파일 마운트 (Task 7~12에서 추가될 static/index.html 등)
    # API 라우트를 모두 등록한 뒤 마지막에 마운트해야 catch-all이 되지 않음
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists() and any(static_dir.iterdir()):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


def _count_links(wiki_root: Path) -> int:
    graph_path = wiki_root / "graph.json"
    if not graph_path.exists():
        return 0
    return len(json.loads(graph_path.read_text()).get("links", []))


def _sanitize_frontmatter(fm: dict) -> dict:
    """date 등 JSON 직렬화 불가 값을 ISO 문자열로 변환."""
    out = {}
    for k, v in fm.items():
        if isinstance(v, (_dt.date, _dt.datetime)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
