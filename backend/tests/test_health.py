from fastapi.testclient import TestClient

from app.main import app


def test_health_does_not_require_database():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documents_health_response():
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/health"]["get"]
    assert "200" in operation["responses"]
    assert "HealthResponse" in schema["components"]["schemas"]


def test_cors_accepts_frontend_origin():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5000"


def test_cors_rejects_unknown_origin():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://example.invalid",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
