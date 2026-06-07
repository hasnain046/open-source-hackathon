# Module: tests.test_auth
# Description: Automated test cases for authentication, password strength validation, and route guards.

from fastapi.testclient import TestClient
from unittest.mock import patch
import uuid
from datetime import datetime
from app.models.user import User

# Define mock user entity for testing
mock_user_id = uuid.uuid4()
mock_user = User(
    id=mock_user_id,
    email="analyst@inflationiq.ai",
    password_hash="mock_bcrypt_hash",
    full_name="Ashfaq",
    role="analyst",
    is_active=True,
    created_at=datetime.utcnow()
)


def test_register_success(client: TestClient):
    """Verify registration succeeds with valid user details and password strength."""
    with patch("app.services.auth_service.AuthService.register_user") as mock_register:
        mock_register.return_value = mock_user
        payload = {
            "email": "analyst@inflationiq.ai",
            "full_name": "Ashfaq",
            "password": "SecurePassword123!",
            "role": "analyst"
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "analyst@inflationiq.ai"
        assert data["full_name"] == "Ashfaq"


def test_register_invalid_password_strength(client: TestClient):
    """Verify registration fails (422) if password fails regular expression strength rules."""
    payload = {
        "email": "analyst@inflationiq.ai",
        "full_name": "Ashfaq",
        "password": "weak",  # Lacks upper, digit, special, and length
        "role": "analyst"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient):
    """Verify login returns access and refresh tokens when credentials are correct."""
    with patch("app.services.auth_service.AuthService.authenticate_user") as mock_auth:
        mock_auth.return_value = mock_user
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "analyst@inflationiq.ai", "password": "SecurePassword123!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Verify login fails (400) when user authentication fails."""
    with patch("app.services.auth_service.AuthService.authenticate_user") as mock_auth:
        mock_auth.return_value = None
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "analyst@inflationiq.ai", "password": "IncorrectPassword"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect email or password."


def test_protected_route_unauthorized(client: TestClient):
    """Verify protected endpoints return 401 if authorization headers are missing."""
    response = client.get("/api/v1/profile/me")
    assert response.status_code == 401


def test_protected_route_authorized(client: TestClient):
    """Verify protected endpoints succeed if valid token is supplied."""
    with patch("app.api.deps.get_current_user") as mock_current_user:
        mock_current_user.return_value = mock_user
        headers = {"Authorization": "Bearer mock_access_token"}
        response = client.get("/api/v1/profile/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "analyst@inflationiq.ai"
