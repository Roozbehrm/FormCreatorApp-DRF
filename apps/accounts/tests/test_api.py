import pytest
from rest_framework.test import APIClient

from apps.accounts.models import OTPPurpose


@pytest.mark.django_db
def test_register_rejects_duplicate_email(user):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/register/",
        {
            "username": "another",
            "email": user.email,
            "password": "StrongPass123!",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens(user):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" not in response.data and "refresh" not in response.data
    assert response.cookies["access"].value
    assert response.cookies["refresh"].value


@pytest.mark.django_db
def test_me_requires_authentication(user):
    client = APIClient()
    assert client.get("/api/v1/auth/me/").status_code == 401
    client.force_authenticate(user=user)
    response = client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.data["username"] == user.username
