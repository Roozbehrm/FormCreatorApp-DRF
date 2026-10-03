import pytest

from apps.categories.models import Category
from apps.forms.models import Form
from apps.processes.models import Process, ProcessStep

PROCESSES_URL = "/api/v1/processes/"


def _process_url(process):
    return f"{PROCESSES_URL}{process.uuid}/"


def _steps_url(process):
    return f"{PROCESSES_URL}{process.uuid}/steps/"





@pytest.mark.django_db
def test_create_process_rejects_step_with_other_users_form(auth_client, other_user):
    """Top-level create: no `process` in context yet, so validate_form falls
    back to the plain "form must be yours" check (lines 18-20)."""
    foreign_form = Form.objects.create(owner=other_user, title="Not mine")

    response = auth_client.post(
        PROCESSES_URL,
        {"title": "P", "type": "free", "steps": [{"form": foreign_form.id, "order": 1}]},
        format="json",
    )

    assert response.status_code == 400
    assert "steps" in response.data["error"]["detail"]


@pytest.mark.django_db
def test_add_step_to_existing_process_rejects_other_users_form(auth_client, user, other_user):
    """Nested /steps/ endpoint: the viewset injects `process` into the
    context, so the "form must belong to the process owner" branch (lines
    16-17) runs instead."""
    process = Process.objects.create(owner=user, title="P", type="free")
    foreign_form = Form.objects.create(owner=other_user, title="Not mine")

    response = auth_client.post(_steps_url(process), {"form": foreign_form.id, "order": 1}, format="json")

    assert response.status_code == 400
    assert "form" in response.data["error"]["detail"]


@pytest.mark.django_db
def test_add_step_with_own_form_succeeds(auth_client, user, form):
    process = Process.objects.create(owner=user, title="P", type="free")

    response = auth_client.post(_steps_url(process), {"form": form.id, "order": 1}, format="json")

    assert response.status_code == 201
    assert ProcessStep.objects.filter(process=process, form=form).exists()





@pytest.mark.django_db
def test_create_process_rejects_other_users_category(auth_client, other_user):
    foreign_category = Category.objects.create(owner=other_user, title="Not mine")

    response = auth_client.post(
        PROCESSES_URL, {"title": "P", "type": "free", "category": foreign_category.id}, format="json"
    )

    assert response.status_code == 400
    assert "category" in response.data["error"]["detail"]


@pytest.mark.django_db
def test_create_process_accepts_own_category(auth_client, user):
    own_category = Category.objects.create(owner=user, title="Mine")

    response = auth_client.post(
        PROCESSES_URL, {"title": "P", "type": "free", "category": own_category.id}, format="json"
    )

    assert response.status_code == 201
    assert response.data["category"] == own_category.id





@pytest.mark.django_db
def test_private_process_requires_access_password_on_create(auth_client):
    response = auth_client.post(PROCESSES_URL, {"title": "P", "type": "free", "visibility": "private"}, format="json")

    assert response.status_code == 400
    assert "access_password" in response.data["error"]["detail"]


@pytest.mark.django_db
def test_private_process_with_password_can_be_created(auth_client):
    response = auth_client.post(
        PROCESSES_URL,
        {"title": "P", "type": "free", "visibility": "private", "access_password": "s3cret"},
        format="json",
    )

    assert response.status_code == 201
    process = Process.objects.get(id=response.data["id"])
    assert process.is_private
    assert process.check_access_password("s3cret")


@pytest.mark.django_db
def test_private_process_password_cannot_be_cleared(auth_client, user):
    process = Process.objects.create(owner=user, title="P", type="free", visibility="private")
    process.set_access_password("s3cret")
    process.save(update_fields=["access_password"])

    response = auth_client.patch(_process_url(process), {"access_password": ""}, format="json")

    assert response.status_code == 400
    assert "access_password" in response.data["error"]["detail"]




@pytest.mark.django_db
def test_create_process_with_nested_steps_sets_order(auth_client, user, form):
    other_form = Form.objects.create(owner=user, title="Second form")

    response = auth_client.post(
        PROCESSES_URL,
        {
            "title": "Onboarding",
            "type": "linear",
            "steps": [{"form": form.id}, {"form": other_form.id}],
        },
        format="json",
    )

    assert response.status_code == 201
    process = Process.objects.get(id=response.data["id"])
    steps = list(process.steps.order_by("order"))
    assert [s.form_id for s in steps] == [form.id, other_form.id]
    assert [s.order for s in steps] == [0, 1]


@pytest.mark.django_db
def test_update_process_replaces_steps_and_password(auth_client, user, form):
    other_form = Form.objects.create(owner=user, title="Second form")
    process = Process.objects.create(owner=user, title="P", type="free", visibility="private")
    process.set_access_password("old-pass")
    process.save(update_fields=["access_password"])
    ProcessStep.objects.create(process=process, form=form, order=0)

    response = auth_client.patch(
        _process_url(process),
        {"steps": [{"form": other_form.id}], "access_password": "new-pass"},
        format="json",
    )

    assert response.status_code == 200
    process.refresh_from_db()
    assert list(process.steps.values_list("form_id", flat=True)) == [other_form.id]
    assert process.check_access_password("new-pass")


@pytest.mark.django_db
def test_update_process_steps_blocked_once_runs_exist(auth_client, user, form):
    process = Process.objects.create(owner=user, title="P", type="free")
    ProcessStep.objects.create(process=process, form=form, order=0)
    process.runs.create(respondent=user, session_key="s1")

    response = auth_client.patch(
        _process_url(process), {"steps": [{"form": form.id, "order": 0}]}, format="json"
    )

    assert response.status_code == 400
    assert "steps" in response.data["error"]["detail"]