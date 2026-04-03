import pytest
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token(username="devd", password="secret123") -> str:
    """Helper — login and return JWT token."""
    response = client.post("/auth/login", json={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]


def test_upload_success():
    token = get_token()
    file_content = b"hello world pdf content"
    response = client.post(
        "/files/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["size_bytes"] == len(file_content)
    assert "devd" in data["message"]


def test_upload_no_token():
    file_content = b"some content"
    response = client.post(
        "/files/upload",
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 403   # no auth header at all


def test_upload_invalid_token():
    response = client.post(
        "/files/upload",
        headers={"Authorization": "Bearer this.is.fake"},
        files={"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 401


def test_upload_disallowed_extension():
    token = get_token()
    response = client.post(
        "/files/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malware.exe", io.BytesIO(b"bad content"), "application/octet-stream")},
    )
    assert response.status_code == 415


def test_upload_no_file():
    token = get_token()
    response = client.post(
        "/files/upload",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422   # missing required field