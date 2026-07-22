import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings


def organization_payload() -> dict[str, str]:
    return {
        "nome": "Instituto Federal de Mato Grosso",
        "sigla": "IFMT",
        "cnpj": "10.784.782/0001-50",
        "esfera": "federal",
        "uf": "MT",
        "municipio": "Cuiabá",
    }


def test_auth_principals_are_loaded_from_environment(monkeypatch) -> None:
    payload = [
        {
            "subject": "reader@ifmt.test",
            "name": "Pessoa Leitora",
            "role": "leitor",
            "token_sha256": "a" * 64,
        }
    ]
    monkeypatch.setenv("AUTH_PRINCIPALS", json.dumps(payload))

    configured = Settings(_env_file=None)

    assert len(configured.auth_principals) == 1
    assert configured.auth_principals[0].subject == "reader@ifmt.test"
    assert configured.auth_principals[0].role == "leitor"

    duplicate = [*payload, {**payload[0], "subject": "other@ifmt.test"}]
    monkeypatch.setenv("AUTH_PRINCIPALS", json.dumps(duplicate))
    with pytest.raises(ValueError, match="token_sha256 duplicado"):
        Settings(_env_file=None)


def test_health_remains_public(unauthenticated_client: TestClient) -> None:
    assert unauthenticated_client.get("/health").status_code == 200
    schema_response = unauthenticated_client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
    assert schema["paths"]["/orgaos"]["get"]["security"] == [{"HTTPBearer": []}]


def test_protected_route_requires_authentication(
    unauthenticated_client: TestClient,
) -> None:
    response = unauthenticated_client.get("/orgaos")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["code"] == "authentication_required"
    assert response.json()["request_id"]


def test_invalid_token_is_rejected(unauthenticated_client: TestClient) -> None:
    response = unauthenticated_client.get(
        "/orgaos",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_required"


def test_reader_can_read_but_cannot_administer(
    unauthenticated_client: TestClient,
    role_headers: dict[str, dict[str, str]],
) -> None:
    assert (
        unauthenticated_client.get(
            "/orgaos", headers=role_headers["leitor"]
        ).status_code
        == 200
    )
    response = unauthenticated_client.post(
        "/orgaos",
        json=organization_payload(),
        headers=role_headers["leitor"],
    )
    assert response.status_code == 403
    assert response.json()["code"] == "access_denied"


def test_analyst_cannot_administer_organizations(
    unauthenticated_client: TestClient,
    role_headers: dict[str, dict[str, str]],
) -> None:
    response = unauthenticated_client.post(
        "/orgaos",
        json=organization_payload(),
        headers=role_headers["analista"],
    )
    assert response.status_code == 403


def test_authenticated_user_without_role_is_denied(
    unauthenticated_client: TestClient,
    role_headers: dict[str, dict[str, str]],
) -> None:
    response = unauthenticated_client.get(
        "/orgaos",
        headers=role_headers["sem_papel"],
    )
    assert response.status_code == 403
    assert response.json()["code"] == "access_denied"

    identity = unauthenticated_client.get(
        "/auth/me",
        headers=role_headers["sem_papel"],
    )
    assert identity.status_code == 200
    assert identity.json()["subject"] == "no-role@ifmt.test"
    assert identity.json()["role"] is None


def test_administrator_can_create_organization(
    unauthenticated_client: TestClient,
    role_headers: dict[str, dict[str, str]],
) -> None:
    response = unauthenticated_client.post(
        "/orgaos",
        json=organization_payload(),
        headers=role_headers["administrador"],
    )
    assert response.status_code == 201
