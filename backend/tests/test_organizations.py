from fastapi.testclient import TestClient

def payload():
    return {"nome": "Instituto Federal de Mato Grosso", "sigla": "ifmt", "cnpj": "10.784.782/0001-50", "esfera": "federal", "uf": "mt", "municipio": "Cuiabá"}

def test_create_organization(client: TestClient):
    response = client.post("/orgaos", json=payload())
    assert response.status_code == 201
    data = response.json()
    assert data["sigla"] == "IFMT"
    assert data["cnpj"] == "10784782000150"
    assert data["uf"] == "MT"

def test_list_organizations(client: TestClient):
    client.post("/orgaos", json=payload())
    response = client.get("/orgaos")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_organization(client: TestClient):
    created = client.post("/orgaos", json=payload()).json()
    response = client.get(f"/orgaos/{created['id']}")
    assert response.status_code == 200

def test_missing_returns_404(client: TestClient):
    assert client.get("/orgaos/999").status_code == 404

def test_duplicate_cnpj_returns_409(client: TestClient):
    assert client.post("/orgaos", json=payload()).status_code == 201
    assert client.post("/orgaos", json=payload()).status_code == 409

def test_invalid_sphere_returns_422(client: TestClient):
    data = payload(); data["esfera"] = "privada"
    assert client.post("/orgaos", json=data).status_code == 422
