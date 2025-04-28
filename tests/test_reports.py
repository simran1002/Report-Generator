import os
from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.report import FileFormat
from tests.test_auth import get_token_headers


@pytest.fixture(scope="module")
def test_input_file():
    """Create a test input file."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    filename = os.path.join(settings.UPLOAD_DIR, "input_test.csv")
    
    data = {
        "field1": ["A", "B", "C"],
        "field2": ["X", "Y", "Z"],
        "field3": ["1", "2", "3"],
        "field4": ["alpha", "beta", "gamma"],
        "field5": [10.0, 20.0, 30.0],
        "refkey1": ["key1", "key2", "key3"],
        "refkey2": ["keyA", "keyB", "keyC"]
    }
    
    pd.DataFrame(data).to_csv(filename, index=False)
    
    yield filename


@pytest.fixture(scope="module")
def test_reference_file():
    """Create a test reference file."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    filename = os.path.join(settings.UPLOAD_DIR, "reference_test.csv")
    
    data = {
        "refkey1": ["key1", "key2", "key3"],
        "refdata1": ["data1", "data2", "data3"],
        "refkey2": ["keyA", "keyB", "keyC"],
        "refdata2": ["dataA", "dataB", "dataC"],
        "refdata3": ["dataX", "dataY", "dataZ"],
        "refdata4": [5.0, 15.0, 25.0]
    }
    
    pd.DataFrame(data).to_csv(filename, index=False)
    
    yield filename


def test_generate_report(test_app: TestClient, test_input_file, test_reference_file):
    """Test generating a report."""
    headers = get_token_headers(test_app)
    
    request = {
        "input_file": os.path.basename(test_input_file),
        "reference_file": os.path.basename(test_reference_file),
        "output_format": "csv",
        "rule_set_id": None 
    }
    
    response = test_app.post("/api/v1/reports/generate", json=request, headers=headers)
    assert response.status_code == 200
    
    report_id = response.json()["id"]
    assert response.json()["status"] == "completed"
    assert response.json()["input_file"] == os.path.basename(test_input_file)
    assert response.json()["reference_file"] == os.path.basename(test_reference_file)
    
    response = test_app.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == report_id
    
    response = test_app.get(f"/api/v1/reports/{report_id}/download", headers=headers)
    assert response.status_code == 200
    
    assert response.headers["content-type"] == "application/octet-stream"


def test_generate_report_invalid_file(test_app: TestClient):
    """Test generating a report with invalid files."""
    headers = get_token_headers(test_app)
    
    request = {
        "input_file": "nonexistent.csv",
        "reference_file": "nonexistent.csv",
        "output_format": "csv",
        "rule_set_id": None
    }
    
    response = test_app.post("/api/v1/reports/generate", json=request, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
