from fastapi.testclient import TestClient


def test_root_redirects_to_consultation(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/consulta"


def test_consultation_page_is_available(client: TestClient) -> None:
    response = client.get("/consulta")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "SIGARP — Consulta de oportunidades" in response.text
    assert "/consulta/assets/app.js" in response.text


def test_consultation_assets_are_available(client: TestClient) -> None:
    script = client.get("/consulta/assets/app.js")
    stylesheet = client.get("/consulta/assets/styles.css")

    assert script.status_code == 200
    assert script.headers["content-type"].startswith("text/javascript")
    assert 'sessionStorage.getItem("sigarp_token")' in script.text
    assert stylesheet.status_code == 200
    assert stylesheet.headers["content-type"].startswith("text/css")
