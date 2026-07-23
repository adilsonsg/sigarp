from fastapi.testclient import TestClient


def test_openapi_exposes_v1_and_marks_legacy_data_routes_deprecated(
    unauthenticated_client: TestClient,
) -> None:
    schema = unauthenticated_client.get("/openapi.json").json()

    expected_paths = {
        "/api/v1/health",
        "/api/v1/auth/me",
        "/api/v1/orgaos",
        "/api/v1/pncp/search",
        "/api/v1/pncp/oportunidades",
        "/api/v1/pncp/oportunidades/execucoes",
    }
    assert expected_paths.issubset(schema["paths"])
    assert schema["paths"]["/orgaos"]["get"]["deprecated"] is True
    assert "deprecated" not in schema["paths"]["/api/v1/orgaos"]["get"]

    operation_ids = [
        operation["operationId"]
        for path in schema["paths"].values()
        for method, operation in path.items()
        if method
        in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
        }
    ]
    assert len(operation_ids) == len(set(operation_ids))


def test_openapi_documents_page_and_standard_error_contracts(
    unauthenticated_client: TestClient,
) -> None:
    schema = unauthenticated_client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/orgaos"]["get"]
    success_content = operation["responses"]["200"]["content"]
    error_content = operation["responses"]["422"]["content"]
    success_schema = next(iter(success_content.values()))["schema"]
    error_schema = next(iter(error_content.values()))["schema"]

    page_name = success_schema["$ref"].rsplit("/", maxsplit=1)[-1]
    page_schema = schema["components"]["schemas"][page_name]
    assert {
        "items",
        "page",
        "page_size",
        "total",
        "total_pages",
    }.issubset(page_schema["properties"])
    assert error_schema["$ref"].endswith("/ErrorResponse")


def test_validation_and_not_found_errors_include_request_id(
    unauthenticated_client: TestClient,
    role_headers: dict[str, dict[str, str]],
) -> None:
    validation = unauthenticated_client.get(
        "/api/v1/orgaos?page=0",
        headers=role_headers["leitor"],
    )
    missing = unauthenticated_client.get("/api/v1/recurso-inexistente")

    assert validation.status_code == 422
    validation_body = validation.json()
    assert validation_body["code"] == "validation_error"
    assert validation_body["errors"]
    assert validation_body["request_id"] == validation.headers["X-Request-ID"]

    assert missing.status_code == 404
    missing_body = missing.json()
    assert missing_body["code"] == "not_found"
    assert missing_body["request_id"] == missing.headers["X-Request-ID"]
