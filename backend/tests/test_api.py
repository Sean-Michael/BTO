from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app import noaa, stations


@pytest.fixture
def fake_noaa(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the NOAA fetch with deterministic extrema (no network)."""

    async def _fake(station_id: str, begin: str, end: str) -> list[noaa.Extremum]:
        base = datetime(2026, 5, 26, 1, 0)
        return [
            noaa.Extremum(
                t=base + timedelta(hours=6 * i),
                height=8.0 if i % 2 == 0 else 2.0,
                kind="H" if i % 2 == 0 else "L",
            )
            for i in range(8)
        ]

    monkeypatch.setattr(noaa, "fetch_extrema", _fake)


def test_list_stations_returns_all_six(client: TestClient) -> None:
    res = client.get("/api/tides/stations")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == len(stations.STATIONS) == 6
    assert {s["id"] for s in body} == {s.id for s in stations.STATIONS}


def test_bootstrap_shape(client: TestClient, fake_noaa: None) -> None:
    res = client.get("/api/tides/bootstrap")
    assert res.status_code == 200
    body = res.json()
    assert body["datum"] == "MLLW"
    assert body["tz"] == "America/Los_Angeles"
    assert "sunrise" in body["sun_moon"]
    assert "moon_glyph" in body["sun_moon"]
    assert len(body["stations"]) == 6
    stn = body["stations"][0]
    assert {"id", "code", "name", "group", "extrema"} <= stn.keys()
    assert stn["extrema"]
    ex = stn["extrema"][0]
    assert {"t", "height", "kind"} <= ex.keys()
    assert isinstance(ex["t"], int)  # epoch ms


def test_bootstrap_drops_failed_station(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, fake_noaa: None
) -> None:
    ok = noaa.fetch_extrema

    async def flaky(station_id: str, begin: str, end: str) -> list[noaa.Extremum]:
        if station_id == stations.STATIONS[0].id:
            raise RuntimeError("NOAA down")
        return await ok(station_id, begin, end)

    monkeypatch.setattr(noaa, "fetch_extrema", flaky)
    body = client.get("/api/tides/bootstrap").json()
    assert len(body["stations"]) == len(stations.STATIONS) - 1


def test_bootstrap_502_when_every_station_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def down(station_id: str, begin: str, end: str) -> list[noaa.Extremum]:
        raise RuntimeError("NOAA down")

    monkeypatch.setattr(noaa, "fetch_extrema", down)
    assert client.get("/api/tides/bootstrap").status_code == 502


def test_fetch_extrema_serves_stale_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    from app.config import Settings

    noaa.clear_cache()
    calls = {"n": 0}
    good = [noaa.Extremum(t=datetime(2026, 5, 27, 1, 0), height=8.0, kind="H")]

    def fake_blocking(station_id: str, begin: str, end: str) -> list[noaa.Extremum]:
        calls["n"] += 1
        if calls["n"] == 1:
            return good
        raise RuntimeError("NOAA down")

    monkeypatch.setattr(noaa, "_fetch_blocking", fake_blocking)
    # cache_ttl=0 forces a refetch on the 2nd call
    monkeypatch.setattr(noaa, "get_settings", lambda: Settings(cache_ttl=0))

    async def run() -> tuple[list[noaa.Extremum], list[noaa.Extremum]]:
        first = await noaa.fetch_extrema("9449211", "20260501", "20260601")
        second = await noaa.fetch_extrema("9449211", "20260501", "20260601")
        return first, second

    first, second = asyncio.run(run())
    assert first == good
    assert second == good  # stale-if-error: last-known-good despite the failure
    noaa.clear_cache()
