from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "application": "SIGARP",
        "version": "0.5.0-alpha6",
        "environment": "development",
        "status": "online",
    }


def test_health_returns_request_id(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "teste-123"},
    )

    assert response.headers["X-Request-ID"] == "teste-123"
