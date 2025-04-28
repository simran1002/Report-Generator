import os
import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.main import app
from app.models.user import User
from app.services.user_service import fake_users_db


@pytest.fixture(scope="module")
def test_app() -> Generator:
    """
    Create a FastAPI TestClient for testing.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def test_user() -> User:
    """
    Get a test user from the fake database.
    """
    return User(**fake_users_db["user"])


@pytest.fixture(scope="module")
def test_superuser() -> User:
    """
    Get a test superuser from the fake database.
    """
    return User(**fake_users_db["admin"])


@pytest.fixture(scope="module")
def test_dirs() -> Generator:
    """
    Create test directories for uploads and reports.
    """
    # Create test directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs(settings.CONFIG_DIR, exist_ok=True)
    
    yield
    
    # Cleanup is not performed to avoid deleting user files
    # In a real test environment, we would use temporary directories
