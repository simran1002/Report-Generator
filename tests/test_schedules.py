import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.report import ScheduleType
from tests.test_auth import get_token_headers


@pytest.fixture(scope="module")
def test_schedule_file():
    """Create a test schedule file."""
    # Ensure the config directory exists
    os.makedirs(settings.CONFIG_DIR, exist_ok=True)
    
    # Create a test schedule file if it doesn't exist
    if not os.path.exists(settings.SCHEDULES_FILE):
        with open(settings.SCHEDULES_FILE, "w") as f:
            f.write("{}")
    
    yield settings.SCHEDULES_FILE


def test_create_schedule(test_app: TestClient, test_schedule_file):
    """Test creating a schedule."""
    headers = get_token_headers(test_app)
    
    # Create a schedule
    request = {
        "name": "Test Schedule",
        "schedule_type": "cron",
        "expression": "0 0 * * *",  # Daily at midnight
        "report_request": {
            "output_format": "csv",
            "rule_set_id": None
        }
    }
    
    response = test_app.post("/api/v1/schedules", params=request, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Schedule"
    assert response.json()["schedule_type"] == "cron"
    assert response.json()["expression"] == "0 0 * * *"
    assert response.json()["enabled"] is True
    
    # Get the schedule ID
    schedule_id = response.json()["id"]
    
    # List schedules
    response = test_app.get("/api/v1/schedules", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Get schedule by ID
    response = test_app.get(f"/api/v1/schedules/{schedule_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == schedule_id
    
    # Update schedule
    request = {
        "name": "Updated Schedule",
        "enabled": False
    }
    
    response = test_app.put(f"/api/v1/schedules/{schedule_id}", params=request, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Schedule"
    assert response.json()["enabled"] is False
    
    # Delete schedule
    response = test_app.delete(f"/api/v1/schedules/{schedule_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Schedule deleted successfully"


def test_create_schedule_invalid_cron(test_app: TestClient, test_schedule_file):
    """Test creating a schedule with an invalid cron expression."""
    headers = get_token_headers(test_app)
    
    # Create a schedule with invalid cron expression
    request = {
        "name": "Invalid Schedule",
        "schedule_type": "cron",
        "expression": "invalid",
        "report_request": {
            "output_format": "csv",
            "rule_set_id": None
        }
    }
    
    response = test_app.post("/api/v1/schedules", params=request, headers=headers)
    assert response.status_code == 400
    assert "Invalid cron expression" in response.json()["detail"]


def test_get_nonexistent_schedule(test_app: TestClient):
    """Test getting a non-existent schedule."""
    headers = get_token_headers(test_app)
    
    response = test_app.get("/api/v1/schedules/nonexistent", headers=headers)
    assert response.status_code == 404
    assert "Schedule not found" in response.json()["detail"]
