import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

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


def test_api_ai_answer_stub(client):
    r = client.post("/api/ai-answer", json={
        "question": "test?",
        "context_slugs": ["habix-profile"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending"
    assert "🚧" in data["message"]
