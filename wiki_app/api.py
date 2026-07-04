"""FastAPI app — 6 endpoints + static mount."""
from __future__ import annotations

import asyncio
import datetime as _dt
import json
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AfterValidator, BaseModel, Field

from wiki_app import access, pages, render, search

# scripts/ 를 sys.path 에 추가해 episode 원장 모듈을 import 한다 (access.py 와 동일
# 컨벤션). wiki_app 은 `python -m wiki_app` 로 실행돼 scripts/ 가 sys.path 에 없을
# 수 있으므로 __file__ 기준 repo 루트에서 경로를 계산한다.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    import episode  # noqa: E402  append-only 에피소드 원장 (PRD US-001/US-002)
except Exception:  # pragma: no cover — 방어적: episode 부재 시 기록만 비활성, 앱은 계속
    episode = None

# LLM 엔진 추상화 (cli|api 분기). subprocess 수명 관리도 여기로 이관됐다.
from lib import llm_client  # noqa: E402
from lib.llm_client import (  # noqa: E402,F401  process 수명 훅 re-export
    LLMError,             # stream 핸들러가 cli 비정상 종료를 event: error 로 표면화
    _kill_process_group,  # 기존 테스트 훅 유지 (api_module._kill_process_group)
    _terminate_proc,      # 기존 테스트 훅 유지 (api_module._terminate_proc)
)


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


def create_app(wiki_root: Path | None = None) -> FastAPI:
    """앱 팩토리 — wiki_root 인자로 test 격리 가능."""
    if wiki_root is None:
        wiki_root = Path(__file__).resolve().parent.parent / "wiki"

    app = FastAPI(title="LLM Wiki", version="0.1.0")
    index = search.Index.build(wiki_root=wiki_root)
    built_at = _dt.datetime.now(_dt.timezone.utc).isoformat()

    # 에피소드 원장은 wiki/ 옆(repo 루트의 episodes/)에 둔다 — 기본 production
    # 경로(repo/episodes)와 동일하고, test 는 tmp wiki_root 로 자동 격리된다.
    _episodes_dir = wiki_root.parent / "episodes"

    def _record_ai_episode(question: str, valid_slugs: list, answer_status: str) -> None:
        """AI 답변 1건을 episode 원장에 append (PRD US-002, **fail-soft**).

        episode 기록 실패는 절대 AI 답변 응답을 깨거나 바꾸지 않는다(US-002 AC·FR-8):
        episode 모듈 부재·스키마 위반·디스크 오류 등 모든 예외를 삼킨다. 양 핸들러의
        `finally` 에서 호출돼 timeout·error·정상 어느 경로든 *최종* status 를 남긴다.
        """
        if episode is None:
            return
        try:
            episode.append(
                {
                    # tz-aware ISO (월별 샤드 도출 + read_recent 정렬에 오프셋 보존)
                    "timestamp": _dt.datetime.now().astimezone().isoformat(),
                    "task_type": "ai_answer",
                    "user_goal": question,
                    "inputs": {"question": question},
                    "read_pages": [f"wiki/{slug}.md" for slug in valid_slugs],
                    "procedures_used": [],
                    "outputs": {"answer_status": answer_status},
                    # 엔드포인트 status → C1 스키마 status 매핑
                    "status": "ok" if answer_status == "done" else answer_status,
                    "notes": "",
                },
                episodes_dir=_episodes_dir,
            )
        except Exception:
            # fail-soft: 원장 기록 실패가 응답 경로를 절대 깨지 않는다.
            pass

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
        """LLM(cli|api 엔진)을 호출해 wiki 페이지 컨텍스트 기반으로 답변 생성.

        엔진 분기·subprocess 수명은 llm_client.call_llm 이 담당한다.
        context_slugs 비어있으면 결과 없음 시나리오 → 사용자 질문만 그대로 전달.
        """
        llm_config = llm_client.load_llm_config()
        # cli 엔진 & CLI 부재 시 graceful fallback (기존 계약)
        if llm_config["engine"] == "cli" and shutil.which("claude") is None:
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

        answer_status = "error"  # finally 에서 기록할 최종 status (성공 시 done 으로 갱신)
        try:
            # 90초 timeout (큰 컨텍스트 + 추론 여유). cli 는 subprocess+process-group
            # 정리, api 는 anthropic SDK 를 llm_client 가 내부에서 처리한다.
            answer = await llm_client.call_llm(
                prompt, config=llm_config, timeout=_AI_ANSWER_TIMEOUT
            )
            answer_status = "done"
        except asyncio.TimeoutError:
            answer_status = "timeout"
            return {
                "status": "timeout",
                "message": f"AI 답변 생성이 {_AI_ANSWER_TIMEOUT}초를 초과해 중단됐어요.",
                "question": req.question,
                "context_slugs": valid_slugs,
                "answer": "",
                "sources": valid_slugs,
            }
        except Exception as e:
            answer_status = "error"
            return {
                "status": "error",
                "message": f"LLM 호출 중 오류: {type(e).__name__}",
                "question": req.question,
                "context_slugs": valid_slugs,
                "answer": "",
                "sources": [],
            }
        finally:
            # 최종 status 로 episode 기록 (fail-soft — 응답에 영향 없음)
            _record_ai_episode(req.question, valid_slugs, answer_status)

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
            llm_config = llm_client.load_llm_config()
            if llm_config["engine"] == "cli" and shutil.which("claude") is None:
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

            # 청크 소스 + subprocess 수명(process-group kill·idle timeout·stderr 동시
            # drain)은 llm_client.stream_llm 이 담당. 여기서는 SSE 계약(meta/chunk/
            # done/error) + *전체* absolute deadline + 누적 chunk/byte cap 만 감싼다.
            agen = None
            answer_status = "error"  # finally 에서 기록할 최종 status (결과 확정 시 갱신)
            try:
                agen = llm_client.stream_llm(
                    prompt, config=llm_config, idle_timeout=_AI_STREAM_IDLE_TIMEOUT
                )
                deadline = time.monotonic() + _AI_STREAM_DEADLINE
                chunk_count = 0
                byte_count = 0
                terminated_early = False  # deadline/cap 으로 끊었는지 (정상 EOF 와 구분)
                async for chunk in agen:
                    if time.monotonic() >= deadline:
                        yield f"event: error\ndata: {_json.dumps({'message': f'AI 답변이 {_AI_STREAM_DEADLINE}초 제한을 초과해 중단됐어요.'}, ensure_ascii=False)}\n\n"
                        terminated_early = True
                        answer_status = "timeout"
                        break
                    if chunk_count >= _AI_STREAM_MAX_CHUNKS or byte_count >= _AI_STREAM_MAX_BYTES:
                        yield f"event: error\ndata: {_json.dumps({'message': 'AI 답변 출력 한도를 초과해 중단됐어요.'}, ensure_ascii=False)}\n\n"
                        terminated_early = True
                        answer_status = "error"
                        break
                    chunk_count += 1
                    byte_count += len(chunk.encode("utf-8"))
                    yield f"event: chunk\ndata: {_json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                if not terminated_early:
                    answer_status = "done"
                    yield "event: done\ndata: {}\n\n"
            except asyncio.TimeoutError:
                # cli readline idle timeout 등 — stream_llm 내부에서 전파
                answer_status = "timeout"
                yield f"event: error\ndata: {_json.dumps({'message': 'AI 답변 생성이 지연돼 중단됐어요.'}, ensure_ascii=False)}\n\n"
            except asyncio.CancelledError:
                # 클라이언트 disconnect — finally 의 aclose 가 child 정리, 그 뒤 전파
                raise
            except LLMError as e:
                # cli 비정상 종료(returncode≠0, stderr) 또는 api 키/패키지 오류 표면화
                answer_status = "error"
                yield f"event: error\ndata: {_json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"
            except Exception as e:
                answer_status = "error"
                yield f"event: error\ndata: {_json.dumps({'message': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"
            finally:
                # timeout·error·정상·disconnect 어디서든 살아있는 child 정리:
                # aclose() 가 stream_llm 의 finally(process-group kill·stderr 회수)를 돌린다.
                if agen is not None:
                    await agen.aclose()
                # 최종 status 로 episode 기록 (fail-soft — 스트림에 영향 없음)
                _record_ai_episode(req.question, valid_slugs, answer_status)

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
