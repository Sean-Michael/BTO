from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Client for an app with no static dir (API-only / dev mode)."""
    return TestClient(create_app(Settings(static_dir=None)))


@pytest.fixture
def static_dir(tmp_path: Path) -> Path:
    """A minimal built-frontend directory: index.html + one asset."""
    (tmp_path / "index.html").write_text("<!doctype html><title>BTO</title>")
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("console.log('bto')")
    return tmp_path


@pytest.fixture
def static_client(static_dir: Path) -> TestClient:
    """Client for an app configured to serve the built frontend."""
    return TestClient(create_app(Settings(static_dir=static_dir)))
