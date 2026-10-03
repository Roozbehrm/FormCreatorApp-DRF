import pytest

from apps.core.exceptions import StepLocked
from apps.forms.models import Field, Form
from apps.forms.services import finalize_submission, start_submission, submit_field_answer
from apps.processes.models import Process, ProcessRun, ProcessStep, RunStatus
from apps.processes.services import assert_step_unlocked, complete_step


@pytest.fixture
def another_form(user):
    return Form.objects.create(owner=user, title="فرم دوم")


@pytest.mark.django_db
def test_linear_process_locks_second_step(user, form, another_form):
    process = Process.objects.create(owner=user, title="P", type="linear")
    first = ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    second = ProcessStep.objects.create(process=process, form=another_form, order=2, is_required=True)
    run = ProcessRun.objects.create(process=process, respondent=user, session_key="run")
    with pytest.raises(StepLocked):
        assert_step_unlocked(run, second)
    Field.objects.create(form=form, type="text", label="A", is_required=True)
    submission = start_submission(form=form, respondent=user, session_key="run", process_run=run)
    submit_field_answer(submission=submission, field=form.fields.get(label="A"), raw="ok")
    finalize_submission(submission)
    complete_step(run, first, submission)
    assert_step_unlocked(run, second)


@pytest.mark.django_db
def test_free_process_allows_any_order(user, form, another_form):
    process = Process.objects.create(owner=user, title="P", type="free")
    ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    second = ProcessStep.objects.create(process=process, form=another_form, order=2, is_required=True)
    run = ProcessRun.objects.create(process=process, respondent=user)
    assert_step_unlocked(run, second)
    submission = start_submission(form=second.form, respondent=user, process_run=run)
    finalize_submission(submission)
    complete_step(run, second, submission)
    assert run.completions.filter(step=second).exists()
    assert run.status == RunStatus.IN_PROGRESS


@pytest.mark.django_db
def test_process_auto_completes_after_required_steps(user, form, another_form):
    process = Process.objects.create(owner=user, title="P", type="free")
    first = ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    ProcessStep.objects.create(process=process, form=another_form, order=2, is_required=False)
    run = ProcessRun.objects.create(process=process, respondent=user)
    submission = start_submission(form=form, respondent=user, process_run=run)
    finalize_submission(submission)
    complete_step(run, first, submission)
    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED
    assert run.completed_at is not None
