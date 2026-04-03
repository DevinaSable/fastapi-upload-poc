import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_success():
    response = client.post("/auth/login", json={
        "username": "devd",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "username": "devd",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_unknown_user():
    response = client.post("/auth/login", json={
        "username": "ghost",
        "password": "secret123"
    })
    assert response.status_code == 401


def test_login_missing_fields():
    response = client.post("/auth/login", json={})
    assert response.status_code == 422   # Pydantic validation error