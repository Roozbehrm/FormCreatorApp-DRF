import pytest
from rest_framework.test import APIClient

from apps.forms.models import Form
from apps.processes.models import Process, ProcessStep, RunStatus


@pytest.mark.django_db
def test_private_process_requires_unlock_and_access_token(user):
    process = Process.objects.create(owner=user, title="Private process", visibility="private")
    process.set_access_password("private-pass")
    process.save(update_fields=["access_password"])
    client = APIClient()
    state_url = f"/api/v1/public/processes/{process.uuid}/state/"

    denied = client.get(state_url)
    unlock = client.post(
        f"/api/v1/public/processes/{process.uuid}/unlock/",
        {"password": "private-pass"},
        format="json",
    )
    allowed = client.get(state_url, HTTP_X_PRIVATE_ACCESS_TOKEN=unlock.data["access_token"])

    assert denied.status_code == 403
    assert unlock.status_code == 200
    assert allowed.status_code == 200


@pytest.mark.django_db
def test_guest_process_run_resumes_with_session_key(user):
    form = Form.objects.create(owner=user, title="Step form")
    next_form = Form.objects.create(owner=user, title="Next step form")
    process = Process.objects.create(owner=user, title="Guest process", type="free")
    first_step = ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    second_step = ProcessStep.objects.create(process=process, form=next_form, order=2, is_required=True)
    client = APIClient()
    state_url = f"/api/v1/public/processes/{process.uuid}/state/"

    initial = client.get(state_url)
    session_key = initial.data["session_key"]
    submitted = client.post(
        f"/api/v1/public/processes/{process.uuid}/steps/{first_step.id}/submit/",
        {"answers": {}},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )
    resumed = client.get(state_url, HTTP_X_SESSION_KEY=session_key)
    finished = client.post(
        f"/api/v1/public/processes/{process.uuid}/steps/{second_step.id}/submit/",
        {"answers": {}},
        format="json",
        HTTP_X_SESSION_KEY=session_key,
    )

    assert initial.status_code == 200
    assert initial.data["session_key"] == session_key
    assert submitted.status_code == 201
    assert submitted.data["run"]["status"] == RunStatus.IN_PROGRESS
    assert resumed.status_code == 200
    assert resumed.data["completed_step_ids"] == [first_step.id]
    assert finished.status_code == 201
    assert finished.data["run"]["status"] == RunStatus.COMPLETED


@pytest.mark.django_db
def test_process_step_cannot_be_submitted_twice(user):
    form = Form.objects.create(owner=user, title="Step form")
    process = Process.objects.create(owner=user, title="Process", type="free")
    step = ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    client = APIClient()
    state_url = f"/api/v1/public/processes/{process.uuid}/state/"
    state = client.get(state_url)
    session_key = state.data["session_key"]
    submit_url = f"/api/v1/public/processes/{process.uuid}/steps/{step.id}/submit/"

    first = client.post(
        submit_url, {"answers": {}}, format="json", HTTP_X_SESSION_KEY=session_key
    )
    second = client.post(
        submit_url, {"answers": {}}, format="json", HTTP_X_SESSION_KEY=session_key
    )

    assert first.status_code == 201
    assert second.status_code == 409
