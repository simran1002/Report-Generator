import os

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.report import TransformationRule, TransformationRuleSet
from tests.test_auth import get_token_headers


@pytest.fixture(scope="module")
def test_rule_file():
    """Create a test rule file."""
    # Ensure the config directory exists
    os.makedirs(settings.CONFIG_DIR, exist_ok=True)
    
    # Create a test rule file if it doesn't exist
    if not os.path.exists(settings.RULES_FILE):
        with open(settings.RULES_FILE, "w") as f:
            f.write("{}")
    
    yield settings.RULES_FILE


def test_get_rules(test_app: TestClient, test_rule_file):
    """Test getting transformation rules."""
    headers = get_token_headers(test_app)
    response = test_app.get("/api/v1/rules", headers=headers)
    assert response.status_code == 200
    assert "rules" in response.json()
    assert "version" in response.json()


def test_update_rules(test_app: TestClient, test_rule_file):
    """Test updating transformation rules."""
    headers = get_token_headers(test_app)
    
    # Create a new rule set
    rule_set = {
        "rules": [
            {
                "output_field": "test_field",
                "expression": "field1 + field2",
                "description": "Test rule"
            }
        ],
        "version": "test"
    }
    
    response = test_app.post("/api/v1/rules", json=rule_set, headers=headers)
    assert response.status_code == 200
    assert response.json()["rules"][0]["output_field"] == "test_field"
    assert response.json()["version"] == "test"
    
    # Get the updated rule set
    response = test_app.get("/api/v1/rules?rule_set_id=test", headers=headers)
    assert response.status_code == 200
    assert response.json()["rules"][0]["output_field"] == "test_field"


def test_validate_rule(test_app: TestClient):
    """Test validating a transformation rule."""
    headers = get_token_headers(test_app)
    
    # Valid rule
    rule = {
        "output_field": "test_field",
        "expression": "field1 + field2",
        "description": "Test rule"
    }
    
    response = test_app.post("/api/v1/rules/validate", json=rule, headers=headers)
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    # Invalid rule
    rule = {
        "output_field": "test_field",
        "expression": "invalid expression",
        "description": "Test rule"
    }
    
    response = test_app.post("/api/v1/rules/validate", json=rule, headers=headers)
    assert response.status_code == 200
    assert response.json()["valid"] is False
