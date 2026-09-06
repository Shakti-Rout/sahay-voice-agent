import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["production_helpline"] == "14566"
    assert "providers" in data


def test_dashboard_stats_endpoint():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "active_calls" in data
    assert "pending_escalations" in data
    assert "risk_breakdown" in data
    assert data["official_helpline"] == "NHAA 14566"


def test_dashboard_sessions_endpoint():
    response = client.get("/api/v1/dashboard/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_escalations_endpoint():
    response = client.get("/api/v1/dashboard/escalations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_acknowledge_escalation():
    response = client.post("/api/v1/dashboard/escalations/call_test_123/acknowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["call_id"] == "call_test_123"


def test_dashboard_ui_html():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "14566" in response.text
    assert "Real-Time AI Trauma & Triage" in response.text


def test_test_console_html():
    response = client.get("/test")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Voice Triage" in response.text
    assert "14566" in response.text
