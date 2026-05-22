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
    def api_ai_answer(req: AIAnswerRequest):
        return {
            "status": "pending",
            "message": "🚧 AI 답변은 다음 버전에서 활성화됩니다. CLI `/query`를 사용해주세요.",
            "question": req.question,
            "context_slugs": req.context_slugs,
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
