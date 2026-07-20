from fastapi.testclient import TestClient


def organization_payload() -> dict[str, str]:
    return {
        "nome": "Instituto Federal de Mato Grosso",
        "sigla": "ifmt",
        "cnpj": "10.784.782/0001-50",
        "esfera": "federal",
        "uf": "mt",
        "municipio": "Cuiabá",
    }


def test_create_organization(client: TestClient) -> None:
    response = client.post("/orgaos", json=organization_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["nome"] == "Instituto Federal de Mato Grosso"
    assert data["sigla"] == "IFMT"
    assert data["cnpj"] == "10784782000150"
    assert data["uf"] == "MT"
    assert data["esfera"] == "federal"


def test_list_organizations(client: TestClient) -> None:
    client.post("/orgaos", json=organization_payload())

    response = client.get("/orgaos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sigla"] == "IFMT"


def test_get_organization_by_id(client: TestClient) -> None:
    created = client.post("/orgaos", json=organization_payload()).json()

    response = client.get(f"/orgaos/{created['id']}")

    assert response.status_code == 200
    assert response.json()["nome"] == "Instituto Federal de Mato Grosso"


def test_get_missing_organization_returns_404(client: TestClient) -> None:
    response = client.get("/orgaos/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Órgão não encontrado."
    assert response.json()["code"] == "resource_not_found"
    assert response.json()["request_id"]


def test_duplicate_cnpj_returns_409(client: TestClient) -> None:
    payload = organization_payload()

    first_response = client.post("/orgaos", json=payload)
    second_response = client.post("/orgaos", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["code"] == "resource_conflict"


def test_invalid_sphere_returns_422(client: TestClient) -> None:
    payload = organization_payload()
    payload["esfera"] = "privada"

    response = client.post("/orgaos", json=payload)

    assert response.status_code == 422


def test_pagination_validation(client: TestClient) -> None:
    response = client.get("/orgaos?limit=500")

    assert response.status_code == 422
