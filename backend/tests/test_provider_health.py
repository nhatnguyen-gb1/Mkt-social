"""
test_provider_health.py — Phase 4: Provider Status & Diagnostic API Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_provider_status_api(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "LIVE_MODE", False)

    response = client.get("/api/v1/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "telephony" in data
    assert "stt" in data
    assert "tts" in data
    assert "llm" in data
    assert data["live_mode"] is False


def test_get_provider_config_api(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "CALLING_PROVIDER", "mock")

    response = client.get("/api/v1/providers/config")
    assert response.status_code == 200
    data = response.json()
    assert data["calling_provider"] == "mock"
    assert "cost_limits" in data
    assert "credentials_configured" in data


def test_post_provider_test_api():
    response = client.post("/api/v1/providers/test", json={"provider_type": "all"})
    assert response.status_code == 200
    data = response.json()
    assert data["tested_target"] == "all"
    assert "results" in data
    assert data["results"]["telephony"]["status"] == "healthy"
