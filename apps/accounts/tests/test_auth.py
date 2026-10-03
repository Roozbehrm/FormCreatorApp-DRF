from unittest.mock import Mock, patch

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_duplicate_email_rejected(api_client, user):
    response = api_client.post(
        "/api/v1/auth/register/",
        {"username": "new", "email": user.email, "password": "pass12345!"},
    )
    assert response.status_code in {400, 409}


@pytest.mark.django_db
def test_login_returns_jwt(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "StrongPass123!"})
    assert response.status_code == 200
    assert "access" not in response.data and "refresh" not in response.data
    assert response.cookies["access"].value
    assert response.cookies["refresh"].value
    assert response.cookies["access"]["httponly"]
    assert response.cookies["refresh"]["httponly"]


@pytest.mark.django_db
def test_login_wrong_password_rejected(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "wrong"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_google_login_sets_http_only_jwt_cookies(api_client, user):
    serializer = Mock()
    serializer.validated_data = {"user": user}
    with patch("apps.accounts.views.GoogleLoginView.get_serializer", return_value=serializer):
        response = api_client.post(
            "/api/v1/auth/social/google/",
            {"access_token": "google-oauth-access-token"},
            format="json",
        )

    assert response.status_code == 200
    assert "access" not in response.data and "refresh" not in response.data
    assert response.cookies["access"]["httponly"]
    assert response.cookies["refresh"]["httponly"]


@pytest.mark.django_db
def test_refresh_rotation_blacklists_old_refresh(api_client, user):
    login = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "StrongPass123!"},
    )
    old_refresh = login.cookies["refresh"].value
    refresh = api_client.post("/api/v1/auth/token/refresh/")
    assert refresh.status_code == 200
    new_refresh = refresh.cookies["refresh"].value
    assert new_refresh != old_refresh
    api_client.cookies["refresh"] = old_refresh
    reused = api_client.post("/api/v1/auth/token/refresh/")
    assert reused.status_code == 401


@pytest.mark.django_db
def test_access_cookie_authenticates_me(api_client, user):
    api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "StrongPass123!"})
    response = api_client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_cookie_auth_requires_csrf_for_unsafe_requests(user):
    client = APIClient(enforce_csrf_checks=True)
    login = client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "StrongPass123!"},
        format="json",
    )
    csrf_token = login.cookies["csrftoken"].value

    rejected = client.patch("/api/v1/auth/me/", {"first_name": "Ali"}, format="json")
    accepted = client.patch(
        "/api/v1/auth/me/",
        {"first_name": "Ali"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert rejected.status_code == 403
    assert accepted.status_code == 200


@pytest.mark.django_db
def test_logout_clears_cookies_and_blacklists_refresh(api_client, user):
    login = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "StrongPass123!"})
    old_refresh = login.cookies["refresh"].value

    response = api_client.post("/api/v1/auth/logout/")

    assert response.status_code == 200
    assert response.cookies["access"]["max-age"] == 0
    assert response.cookies["refresh"]["max-age"] == 0
    api_client.cookies["refresh"] = old_refresh
    reused = api_client.post("/api/v1/auth/token/refresh/")
    assert reused.status_code == 401


@pytest.mark.django_db
def test_unverified_user_cannot_password_login(api_client, user):
    user.is_verified = False
    user.save(update_fields=["is_verified"])
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 403
    assert response.data["error"]["code"] == "user_not_verified"


@pytest.mark.django_db
def test_password_reset_changes_password_without_logging_in(api_client, user, settings):
    from apps.accounts import services
    from apps.accounts.models import OTPPurpose

    code = services.generate_otp(user.email, OTPPurpose.RESET)
    response = api_client.post(
        "/api/v1/auth/password/reset/",
        {
            "identifier": user.email,
            "purpose": OTPPurpose.RESET,
            "code": code,
            "new_password": "NewStrongPass123!",
        },
        format="json",
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123!")
    assert "access" not in response.cookies
    assert "refresh" not in response.cookies
