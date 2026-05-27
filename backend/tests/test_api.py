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
    res = client.get("/api/stations")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == len(stations.STATIONS) == 6
    assert {s["id"] for s in body} == {s.id for s in stations.STATIONS}


def test_bootstrap_shape(client: TestClient, fake_noaa: None) -> None:
    res = client.get("/api/bootstrap")
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
