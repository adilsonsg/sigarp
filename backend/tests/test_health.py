from fastapi.testclient import TestClient

from app.core.config import settings


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "application": "SIGARP",
        "version": "0.12.0-alpha1",
        "environment": settings.app_env,
        "status": "online",
    }


def test_health_returns_request_id(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "teste-123"},
    )

    assert response.headers["X-Request-ID"] == "teste-123"
