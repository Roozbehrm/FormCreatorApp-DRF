import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_duplicate_email_rejected(api_client, user):
    url = "/api/v1/auth/register/"
    response = api_client.post(url, {"username": "new", "email": user.email, "password": "StrongPass123!"})
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_jwt(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "pass12345!"})
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data


@pytest.mark.django_db
def test_login_wrong_password_rejected(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "wrong"})
    assert response.status_code == 401
