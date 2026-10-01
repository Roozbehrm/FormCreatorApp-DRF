import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def user(db, django_user_model):
    return UserFactory()


@pytest.fixture
def other_user(db, django_user_model):
    return UserFactory(username="ali", email="ali@example.com")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def form(db, user):
    from apps.forms.models import Form

    return Form.objects.create(owner=user, title="فرم تست")
