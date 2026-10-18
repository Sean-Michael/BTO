from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.config import Settings, get_settings

# Everything lives under /tides (UI) and /api/tides (API) so the app can sit
# behind sean-michael.dev's Traefik next to the main site without path clashes.
BASE = "/tides"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title="Bellingham Tidal Observatory", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/tides/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router)

    # Serve the built frontend when a static dir is configured and present.
    # In development this is left unset and Vite serves the UI on :5173.
    if settings.static_dir and settings.static_dir.is_dir():
        assets = settings.static_dir / "assets"
        if assets.is_dir():
            app.mount(f"{BASE}/assets", StaticFiles(directory=assets), name="assets")

        static_root = settings.static_dir.resolve()
        index_file = static_root / "index.html"

        @app.get("/", include_in_schema=False)
        def root() -> RedirectResponse:
            return RedirectResponse(BASE)

        @app.get(BASE, include_in_schema=False)
        @app.get(BASE + "/{full_path:path}", include_in_schema=False)
        def spa(full_path: str = "") -> FileResponse:
            # Top-level files from frontend/public (favicon, background image).
            candidate = (static_root / full_path).resolve()
            if (
                full_path
                and candidate.is_relative_to(static_root)
                and candidate.is_file()
            ):
                return FileResponse(candidate)
            # Single-page app fallback. index.html points at the current hashed
            # bundles, so always revalidate it.
            return FileResponse(index_file, headers={"Cache-Control": "no-cache"})

    return app


app = create_app()
