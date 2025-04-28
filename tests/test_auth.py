from fastapi.testclient import TestClient


def test_login(test_app: TestClient):
    """Test the login endpoint with valid credentials."""
    response = test_app.post(
        "/api/v1/auth/login",
        data={"username": "user", "password": "user"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(test_app: TestClient):
    """Test the login endpoint with invalid credentials."""
    response = test_app.post(
        "/api/v1/auth/login",
        data={"username": "user", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def get_token_headers(test_app: TestClient):
    """Helper function to get authentication headers."""
    response = test_app.post(
        "/api/v1/auth/login",
        data={"username": "user", "password": "user"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
