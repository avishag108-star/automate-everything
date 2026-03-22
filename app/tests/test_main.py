"""Unit tests for StatusWatch API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "StatusWatch" in response.json()["message"]


def test_check_valid_url():
    response = client.post("/check", json={"url": "https://google.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["up", "down"]
    assert "url" in data
    assert "checked_at" in data


def test_check_unreachable_url():
    response = client.post(
        "/check", json={"url": "http://this-definitely-does-not-exist-12345.com", "timeout": 2}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "down"
