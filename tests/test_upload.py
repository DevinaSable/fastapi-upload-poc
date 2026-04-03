import io
import pytest


def test_upload_success(client, auth_headers):
    content = b"hello world pdf content"
    response = client.post(
        "/files/upload",
        headers=auth_headers,
        files={"file": ("test.pdf", io.BytesIO(content), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["size_bytes"] == len(content)
    assert "devd" in data["message"]
    assert "storage_path" in data


def test_upload_no_token(client):
    response = client.post(
        "/files/upload",
        files={"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 403


def test_upload_invalid_token(client):
    response = client.post(
        "/files/upload",
        headers={"Authorization": "Bearer this.is.fake"},
        files={"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 401


def test_upload_disallowed_extension(client, auth_headers):
    response = client.post(
        "/files/upload",
        headers=auth_headers,
        files={"file": ("malware.exe", io.BytesIO(b"bad"), "application/octet-stream")},
    )
    assert response.status_code == 415


def test_upload_no_file(client, auth_headers):
    response = client.post(
        "/files/upload",
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_upload_expired_token(client):
    """Tampered token must be rejected."""
    response = client.post(
        "/files/upload",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.fake.payload"},
        files={"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 401