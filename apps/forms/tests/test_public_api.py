import pytest
from rest_framework.test import APIClient

from apps.forms.models import Field


@pytest.mark.django_db
def test_public_form_schema_does_not_expose_owner(api_client, form):
    response = api_client.get(f"/api/v1/public/forms/{form.uuid}/")

    assert response.status_code == 200
    assert response.data["uuid"] == str(form.uuid)
    assert "owner" not in response.data
    assert "access_password" not in response.data


@pytest.mark.django_db
def test_private_form_requires_unlock_token(api_client, form):
    form.visibility = "private"
    form.set_access_password("private-pass")
    form.save()

    denied = api_client.get(f"/api/v1/public/forms/{form.uuid}/")
    unlocked = api_client.post(
        f"/api/v1/public/forms/{form.uuid}/unlock/",
        {"password": "private-pass"},
        format="json",
    )
    token = unlocked.data["access_token"]
    allowed = api_client.get(
        f"/api/v1/public/forms/{form.uuid}/",
        HTTP_X_PRIVATE_ACCESS_TOKEN=token,
    )

    assert denied.status_code == 403
    assert unlocked.status_code == 200
    assert allowed.status_code == 200


@pytest.mark.django_db
def test_public_submission_saves_answers_incrementally(api_client, form):
    field = Field.objects.create(form=form, type="text", label="Name", is_required=True)
    started = api_client.post(f"/api/v1/public/forms/{form.uuid}/start/", {}, format="json")
    submission_id = started.data["submission_id"]
    session_key = started.data["session_key"]

    answer = api_client.post(
        f"/api/v1/public/forms/{form.uuid}/submissions/{submission_id}/answer/{field.id}/",
        {"answer": "Ada"},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )
    assert answer.status_code == 200
    assert field.answers.get(submission_id=submission_id).value_text == "Ada"

    finalized = api_client.post(
        f"/api/v1/public/forms/{form.uuid}/submissions/{submission_id}/finalize/",
        {},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )

    assert finalized.status_code == 200
    assert finalized.data["is_complete"] is True


@pytest.mark.django_db
def test_guest_cannot_choose_initial_session_key(api_client, form):
    response = api_client.post(
        f"/api/v1/public/forms/{form.uuid}/start/",
        {"session_key": "client-chosen-key"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_completed_submission_cannot_be_edited(api_client, form):
    field = Field.objects.create(form=form, type="text", label="Name", is_required=True)
    started = api_client.post(f"/api/v1/public/forms/{form.uuid}/start/", {}, format="json")
    submission_id = started.data["submission_id"]
    session_key = started.data["session_key"]

    api_client.post(
        f"/api/v1/public/forms/{form.uuid}/submissions/{submission_id}/answer/{field.id}/",
        {"answer": "Ada"},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )
    api_client.post(
        f"/api/v1/public/forms/{form.uuid}/submissions/{submission_id}/finalize/",
        {},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )

    rejected = api_client.post(
        f"/api/v1/public/forms/{form.uuid}/submissions/{submission_id}/answer/{field.id}/",
        {"answer": "Grace"},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )
    assert rejected.status_code == 409


@pytest.mark.django_db
def test_field_cannot_be_deleted_after_completed_submission(api_client, form):
    field = Field.objects.create(form=form, type="text", label="Name")
    from apps.forms.models import Submission
    Submission.objects.create(form=form, is_complete=True)
    api_client.force_authenticate(user=form.owner)

    response = api_client.delete(
        f"/api/v1/forms/{form.uuid}/fields/{field.id}/"
    )
    assert response.status_code == 409
