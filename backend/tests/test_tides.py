from datetime import datetime, timedelta

from app import tides
from app.noaa import Extremum


def _curve() -> list[Extremum]:
    base = datetime(2026, 5, 26, 0, 0)
    return [
        Extremum(t=base + timedelta(hours=1), height=8.0, kind="H"),
        Extremum(t=base + timedelta(hours=7), height=2.0, kind="L"),
        Extremum(t=base + timedelta(hours=13), height=7.0, kind="H"),
        Extremum(t=base + timedelta(hours=19), height=3.0, kind="L"),
    ]


def test_height_at_extrema_matches_exactly() -> None:
    c = _curve()
    assert abs(tides.height_at(c, c[0].t) - 8.0) < 1e-6
    assert abs(tides.height_at(c, c[1].t) - 2.0) < 1e-6


def test_height_at_midpoint_is_mean() -> None:
    c = _curve()
    mid = c[0].t + (c[1].t - c[0].t) / 2
    assert abs(tides.height_at(c, mid) - 5.0) < 1e-6  # (8+2)/2


def test_rate_sign_tracks_direction() -> None:
    c = _curve()
    # Falling segment between first high and first low.
    mid = c[0].t + (c[1].t - c[0].t) / 2
    assert tides.rate_at(c, mid) < 0
    # Rising segment between first low and second high.
    mid2 = c[1].t + (c[2].t - c[1].t) / 2
    assert tides.rate_at(c, mid2) > 0


def test_snapshot_reports_next_events_and_day_range() -> None:
    c = _curve()
    now = c[0].t + timedelta(hours=2)  # just after first high, falling
    snap = tides.snapshot(c, now)
    assert snap.trend == "falling"
    assert snap.next_low is c[1]
    assert snap.next_high is c[2]
    assert abs(snap.day_max - 8.0) < 1e-6
    assert abs(snap.day_min - 2.0) < 1e-6


def test_sample_spans_window_inclusive() -> None:
    c = _curve()
    start, end = c[0].t, c[3].t
    pts = tides.sample(c, start, end, n=10)
    assert len(pts) == 11
    assert pts[0].t == start
    assert pts[-1].t == end
