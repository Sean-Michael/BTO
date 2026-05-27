# Bellingham Tidal Observatory (BTO)

A Grafana/Ganglia-style dashboard for the tides of the inner Salish Sea. It pulls
real hi/lo predictions from the [NOAA CO-OPS API](https://api.tidesandcurrents.noaa.gov/api/prod/)
for the Bellingham Bay / San Juan stations, interpolates a smooth tide curve, and
renders a dense, customizable observatory view (station grid, focus drilldown,
compare overlay, time ranges, density, grouping).

- **Frontend** — React + TypeScript + Vite (`frontend/`)
- **Backend** — FastAPI on a `uv` environment, wrapping `noaa_coops` (`backend/`)

## Development

### With Docker Compose (recommended)

Runs both services with hot-reload:

```bash
docker compose up --build
```

- UI: http://localhost:5173
- API: http://localhost:8000

### Without Docker

Backend:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Frontend (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to the backend on port 8000.

## Production build

The root [Dockerfile](Dockerfile) builds the frontend and serves it as static
files from FastAPI in a single container:

```bash
docker build -t bto .
docker run -p 8000:8000 bto
```

The app is then available at http://localhost:8000.

## Configuration

Backend settings come from `backend/.env` (all prefixed `BTO_`). Copy the example:

```bash
cp backend/.env.example backend/.env
```

| Variable           | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `BTO_STATIC_DIR`   | Path to the built frontend; serves the UI when set.    |
| `BTO_CORS_ORIGINS` | Allowed CORS origins (JSON list).                      |
| `BTO_CACHE_TTL`    | Seconds to cache NOAA prediction responses in-memory.  |

## Data notes

The tide curve is built by half-cosine interpolation between **real NOAA hi/lo
predictions** (reliable across both harmonic and subordinate stations). Sun/moon
facts are computed with `astral`. NOAA's prediction feed has no solunar or
per-station weather data, so the focus panel's secondary slots show real
sun/moon and station metadata rather than the prototype's invented values.

## Stations List

NOAA has provided the following stations within the Bellingham Bay:

| Name                            | Id      | Lat      | Lon       | Predictions |
| ------------------------------- | ------- | -------- | --------- | ----------- |
| Bellingham                      | 9449211 | +48.7450 | -122.4950 | Subordinate |
| Village Point, Lummi Island     | 9449161 | +48.7167 | -122.7080 | Harmonic    |
| Sandy Point, Lummi Bay          | 9449292 | +48.7900 | -122.7080 | Subordinate |
| Rosario, East Sound, Orcas Island | 9449771 | +48.6467 | -122.8700 | Harmonic    |
| Upright Head, Lopez Island      | 9449911 | +48.5717 | -122.8850 | Harmonic    |
| Orcas, Orcas Island             | 9449798 | +48.6000 | -122.9500 | Subordinate |


### Resources

I found [this reddit post](https://www.reddit.com/r/oceanography/comments/i0e8m5/calculation_of_subordinate_tide_stations_from/) helpful for understanding the Subordinate/Harmonic `Predictions` column. The Bellingham station data is an interpolation (estimate of unkown values from known values) of the readings from Port Townsend, and the curves are rendered as Bezier curves between the high and low points. That really takes me back to my Intro To Computer Graphics days at OSU. This would have been such a cool project for that assignment! Oh well.

