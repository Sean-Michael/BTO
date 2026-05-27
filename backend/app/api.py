"""Bellingham Tidal Observatory REST API.

A single ``/api/bootstrap`` call returns everything the dashboard needs: station
metadata plus real NOAA hi/lo predictions (extrema) spanning a wide window, plus
sun/moon facts. The frontend interpolates the smooth tide curve from those
extrema client-side, so range/density/hover changes need no further round trips.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException

from app import astro, noaa, stations

router = APIRouter(prefix="/api")

_TZ = ZoneInfo("America/Los_Angeles")

# How far around "now" to fetch hi/lo predictions — wide enough to cover the
# dashboard's longest range (30D) panned either direction.
_PAST_DAYS = 20
_FUTURE_DAYS = 20


def _epoch_ms(dt: datetime) -> int:
    # NOAA lst_ldt times are Pacific wall-clock but tz-naive; localize them.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_TZ)
    return int(dt.timestamp() * 1000)


def _serialize_extrema(extrema: list[noaa.Extremum]) -> list[dict[str, Any]]:
    return [
        {"t": _epoch_ms(e.t), "height": round(e.height, 3), "kind": e.kind}
        for e in extrema
    ]


async def _station_payload(s: stations.Station, begin: str, end: str) -> dict[str, Any]:
    extrema = await noaa.fetch_extrema(s.id, begin, end)
    return {
        "id": s.id,
        "code": s.code,
        "name": s.name,
        "area": s.area,
        "lat": s.lat,
        "lon": s.lon,
        "predictions": s.predictions,
        "group": s.group,
        "extrema": _serialize_extrema(extrema),
    }


async def _bootstrap() -> dict[str, Any]:
    now = datetime.now(_TZ)
    begin = (now - timedelta(days=_PAST_DAYS)).strftime("%Y%m%d")
    end = (now + timedelta(days=_FUTURE_DAYS)).strftime("%Y%m%d")

    payloads = await asyncio.gather(
        *(_station_payload(s, begin, end) for s in stations.STATIONS)
    )

    sm = astro.sun_moon(now.date())
    return {
        "now": _epoch_ms(now),
        "tz": "America/Los_Angeles",
        "datum": "MLLW",
        "units": "english",
        "date": {
            "iso": now.strftime("%Y-%m-%d"),
            "pretty": now.strftime("%a · %b %-d, %Y"),
        },
        "sun_moon": {
            "sunrise": sm.sunrise,
            "sunset": sm.sunset,
            "noon": sm.noon,
            "moon_phase": sm.moon_phase,
            "moon_illum": sm.moon_illum,
            "moon_glyph": sm.moon_glyph,
        },
        "stations": list(payloads),
    }


@router.get("/bootstrap")
async def bootstrap() -> dict[str, Any]:
    """Everything the frontend loads on startup, in one round trip."""
    try:
        return await _bootstrap()
    except Exception as exc:  # noqa: BLE001 — surface upstream NOAA failures cleanly
        raise HTTPException(
            status_code=502, detail=f"NOAA upstream error: {exc}"
        ) from exc


@router.get("/stations")
def list_stations() -> list[dict[str, Any]]:
    return [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "area": s.area,
            "lat": s.lat,
            "lon": s.lon,
            "predictions": s.predictions,
            "group": s.group,
        }
        for s in stations.STATIONS
    ]
