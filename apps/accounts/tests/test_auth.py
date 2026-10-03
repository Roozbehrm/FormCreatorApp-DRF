import pytest


@pytest.mark.django_db
def test_register_duplicate_email_rejected(api_client, user):
    response = api_client.post(
        "/api/v1/auth/register/",
        {"username": "new", "email": user.email, "password": "pass12345!"},
    )
    assert response.status_code in {400, 409}


@pytest.mark.django_db
def test_login_returns_jwt(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "pass12345!"})
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data


@pytest.mark.django_db
def test_login_wrong_password_rejected(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"username": user.username, "password": "wrong"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_rotation_blacklists_old_refresh(api_client, user):
    login = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "pass12345!"},
    )
    old_refresh = login.data["refresh"]
    refresh = api_client.post("/api/v1/auth/token/refresh/", {"refresh": old_refresh})
    assert refresh.status_code == 200
    assert refresh.data["refresh"] != old_refresh
    reused = api_client.post("/api/v1/auth/token/refresh/", {"refresh": old_refresh})
    assert reused.status_code == 401
