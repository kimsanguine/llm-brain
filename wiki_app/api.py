"""FastAPI app — 4 endpoints + static mount."""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from wiki_app import access, pages, render, search


class AIAnswerRequest(BaseModel):
    question: str
    context_slugs: list[str] = []


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
        import asyncio
        import shutil

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

        # 컨텍스트 페이지 본문 수집
        context_chunks = []
        valid_slugs = []
        for slug in req.context_slugs[:5]:  # 최대 5개 (토큰 제어)
            try:
                page = pages.load_page(slug, wiki_root=wiki_root)
                context_chunks.append(f"## {slug}\n\n{page['body_md']}")
                valid_slugs.append(slug)
            except pages.PageNotFound:
                continue

        context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(컨텍스트 페이지 없음)"
        prompt = (
            "다음 wiki 페이지 컨텍스트만 사용해 사용자 질문에 답변해주세요. "
            "컨텍스트에 없는 사실은 추측하지 말고 '관련 정보 없음'으로 답하세요.\n\n"
            f"# 사용자 질문\n{req.question}\n\n"
            f"# 컨텍스트\n{context}"
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", "-p", prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # 90초 timeout (큰 컨텍스트 + 추론 여유)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "message": "AI 답변 생성이 90초를 초과해 중단됐어요.",
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
        import asyncio
        import json as _json
        import shutil

        async def event_gen():
            if shutil.which("claude") is None:
                yield f"event: error\ndata: {_json.dumps({'message': 'Claude Code CLI 없음'}, ensure_ascii=False)}\n\n"
                return

            # context 수집 (기존 로직과 동일)
            context_chunks = []
            valid_slugs = []
            for slug in req.context_slugs[:5]:
                try:
                    page = pages.load_page(slug, wiki_root=wiki_root)
                    context_chunks.append(f"## {slug}\n\n{page['body_md']}")
                    valid_slugs.append(slug)
                except pages.PageNotFound:
                    continue

            yield f"event: meta\ndata: {_json.dumps({'context_slugs': valid_slugs}, ensure_ascii=False)}\n\n"

            context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(컨텍스트 페이지 없음)"
            prompt = (
                "다음 wiki 페이지 컨텍스트만 사용해 사용자 질문에 답변해주세요. "
                "컨텍스트에 없는 사실은 추측하지 말고 '관련 정보 없음'으로 답하세요.\n\n"
                f"# 사용자 질문\n{req.question}\n\n"
                f"# 컨텍스트\n{context}"
            )

            try:
                proc = await asyncio.create_subprocess_exec(
                    "claude", "-p", prompt,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                # stdout을 라인 단위로 streaming
                assert proc.stdout is not None
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    text = line.decode("utf-8", errors="replace")
                    yield f"event: chunk\ndata: {_json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                await proc.wait()
                yield "event: done\ndata: {}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {_json.dumps({'message': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"

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
