import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-app-backend"


def test_readiness_endpoint():
    """Test the readiness check endpoint."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "environment" in data


def test_chat_endpoint_valid_message():
    """Test chat endpoint with valid message."""
    response = client.post(
        "/api/chat",
        json={"message": "Hello, AI!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "trace_id" in data
    assert len(data["trace_id"]) > 0


def test_chat_endpoint_empty_message():
    """Test chat endpoint with empty message."""
    response = client.post(
        "/api/chat",
        json={"message": ""}
    )
    assert response.status_code == 400


def test_request_id_header():
    """Test that request ID is added to response headers."""
    response = client.get("/api/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

# Made with Bob
