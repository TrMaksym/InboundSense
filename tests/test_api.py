import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.scraper import extract_clean_text


@pytest_asyncio.fixture(loop_scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_analytics_stats_endpoint(client):
    response = await client.get("/api/v1/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "total_chunks" in data
    assert isinstance(data["events_by_category"], dict)


@pytest.mark.asyncio
async def test_create_event_endpoint(client):
    payload = {"text": "Integration test event text for pipeline"}
    response = await client.post("/api/v1/events/", json=payload)
    assert response.status_code in (200, 201, 202)
    data = response.json()
    assert data["text"] == payload["text"]
    assert "id" in data


def test_scraper_extract_clean_text():
    html_content = """
    <html>
        <head><title>Test</title><style>.hidden {display: none;}</style></head>
        <body>
            <header>Header content</header>
            <main>
                <article>
                    <h1>Valid Title</h1>
                    <p>Clean text body for testing.</p>
                </article>
            </main>
            <script>console.log("drop me");</script>
        </body>
    </html>
    """
    clean_text = extract_clean_text(html_content)
    assert "Valid Title" in clean_text
    assert "Clean text body for testing." in clean_text
    assert "console.log" not in clean_text
    assert "Header content" not in clean_text


@pytest.mark.asyncio
async def test_stream_search_endpoint(client):
    response = await client.get("/api/v1/stream/search", params={"q": "database error"})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "data:" in response.text


@pytest.mark.asyncio
async def test_search_endpoint(client):
    payload = {"query": "database error", "limit": 3}
    response = await client.post("/api/v1/search/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert isinstance(data["results"], list)