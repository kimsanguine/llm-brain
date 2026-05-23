"""FastAPI app — 4 endpoints + static mount."""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
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
