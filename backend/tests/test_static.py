from fastapi.testclient import TestClient


def test_api_health_still_works_with_static(static_client: TestClient) -> None:
    res = static_client.get("/api/tides/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_root_redirects_to_tides(static_client: TestClient) -> None:
    res = static_client.get("/", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/tides"


def test_tides_serves_index_html(static_client: TestClient) -> None:
    res = static_client.get("/tides")
    assert res.status_code == 200
    assert "<title>BTO</title>" in res.text
    assert res.headers["cache-control"] == "no-cache"


def test_unknown_route_under_tides_falls_back_to_index(
    static_client: TestClient,
) -> None:
    # SPA client-side routing: any path under /tides returns index.html.
    res = static_client.get("/tides/some/view")
    assert res.status_code == 200
    assert "<title>BTO</title>" in res.text


def test_paths_outside_tides_are_not_ours(static_client: TestClient) -> None:
    # The main site owns everything else on the domain.
    assert static_client.get("/blog").status_code == 404


def test_assets_are_served(static_client: TestClient) -> None:
    res = static_client.get("/tides/assets/app.js")
    assert res.status_code == 200
    assert "bto" in res.text


def test_no_static_dir_has_no_spa_fallback(client: TestClient) -> None:
    # Without a static dir there is no catch-all; unknown routes 404.
    res = client.get("/tides")
    assert res.status_code == 404


def test_public_files_are_served(static_client: TestClient) -> None:
    res = static_client.get("/tides/favicon.svg")
    assert res.status_code == 200
    assert res.text == "<svg/>"


def test_path_traversal_gets_index_not_file(static_client: TestClient) -> None:
    res = static_client.get("/tides/..%2F..%2Fetc%2Fpasswd")
    assert "<title>BTO</title>" in res.text
