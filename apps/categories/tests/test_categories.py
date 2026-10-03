import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.core.exceptions import DomainError
from apps.forms.models import Form
from apps.processes.models import Process


@pytest.mark.django_db
def test_category_unique_at_same_level_but_allowed_under_another_parent(user):
    Category.objects.create(owner=user, title="Shared")
    parent = Category.objects.create(owner=user, title="Parent")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Category.objects.create(owner=user, title="Shared")

    nested = Category.objects.create(owner=user, title="Shared", parent=parent)
    assert nested.parent == parent


@pytest.mark.django_db
def test_category_rejects_cycles(user):
    parent = Category.objects.create(owner=user, title="Parent")
    child = Category.objects.create(owner=user, title="Child", parent=parent)
    parent.parent = child

    with pytest.raises(DomainError) as exc_info:
        parent.save()

    assert exc_info.value.code == "category_cycle"


@pytest.mark.django_db
def test_other_users_category_is_hidden(api_client, user, other_user):
    category = Category.objects.create(owner=other_user, title="Private category")
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/v1/categories/{category.pk}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_form_and_process_lists_filter_by_category(api_client, user):
    selected = Category.objects.create(owner=user, title="Selected")
    other = Category.objects.create(owner=user, title="Other")
    Form.objects.create(owner=user, title="Selected form", category=selected)
    Form.objects.create(owner=user, title="Other form", category=other)
    Process.objects.create(owner=user, title="Selected process", category=selected)
    Process.objects.create(owner=user, title="Other process", category=other)
    api_client.force_authenticate(user=user)

    forms = api_client.get(f"/api/v1/forms/?category={selected.pk}")
    processes = api_client.get(f"/api/v1/processes/?category={selected.pk}")

    assert forms.status_code == 200
    assert [item["title"] for item in forms.data["results"]] == ["Selected form"]
    assert processes.status_code == 200
    assert [item["title"] for item in processes.data["results"]] == ["Selected process"]
