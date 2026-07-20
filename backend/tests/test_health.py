from fastapi.testclient import TestClient

def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"application": "SIGARP", "version": "0.2.0", "status": "online"}
