import os
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.test_auth import get_token_headers


@pytest.fixture(scope="module")
def test_csv_file():
    """Create a test CSV file for upload."""
    content = b"field1,field2,field3,field4,field5,refkey1,refkey2\nA,X,1,alpha,10.0,key1,keyA\n"
    return ("test.csv", BytesIO(content))


def test_upload_file(test_app: TestClient, test_csv_file):
    """Test uploading a file."""
    headers = get_token_headers(test_app)
    
    # Upload file
    filename, file_content = test_csv_file
    response = test_app.post(
        "/api/v1/files/upload/input",
        files={"file": (filename, file_content, "text/csv")},
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["file_type"] == "input"
    
    # Get the uploaded filename
    uploaded_filename = response.json()["filename"]
    
    # List files
    response = test_app.get("/api/v1/files/list/input", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Download file
    response = test_app.get(f"/api/v1/files/download/{uploaded_filename}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


def test_upload_invalid_file_type(test_app: TestClient, test_csv_file):
    """Test uploading a file with an invalid file type."""
    headers = get_token_headers(test_app)
    
    # Upload file with invalid file type
    filename, file_content = test_csv_file
    response = test_app.post(
        "/api/v1/files/upload/invalid",
        files={"file": (filename, file_content, "text/csv")},
        headers=headers
    )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_list_all_files(test_app: TestClient):
    """Test listing all files."""
    headers = get_token_headers(test_app)
    
    response = test_app.get("/api/v1/files/list", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_download_nonexistent_file(test_app: TestClient):
    """Test downloading a non-existent file."""
    headers = get_token_headers(test_app)
    
    response = test_app.get("/api/v1/files/download/nonexistent.csv", headers=headers)
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]
