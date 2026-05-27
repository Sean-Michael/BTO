from fastapi.testclient import TestClient


def test_api_health_still_works_with_static(static_client: TestClient) -> None:
    res = static_client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_root_serves_index_html(static_client: TestClient) -> None:
    res = static_client.get("/")
    assert res.status_code == 200
    assert "<title>BTO</title>" in res.text


def test_unknown_route_falls_back_to_index(static_client: TestClient) -> None:
    # SPA client-side routing: any non-API path returns index.html.
    res = static_client.get("/tides")
    assert res.status_code == 200
    assert "<title>BTO</title>" in res.text


def test_assets_are_served(static_client: TestClient) -> None:
    res = static_client.get("/assets/app.js")
    assert res.status_code == 200
    assert "bto" in res.text


def test_no_static_dir_has_no_spa_fallback(client: TestClient) -> None:
    # Without a static dir there is no catch-all; unknown routes 404.
    res = client.get("/tides")
    assert res.status_code == 404
