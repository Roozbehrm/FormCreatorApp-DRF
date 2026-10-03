import pytest

from apps.core.exceptions import DomainError, StepLocked
from apps.forms.models import Form, Submission
from apps.processes.models import Process, ProcessRun, ProcessStep, RunStatus, StepCompletion
from apps.processes.services import (
    assert_step_unlocked,
    complete_step,
    complete_step_for_submission,
    next_step_for_run,
)


@pytest.fixture
def linear_process(user, form):
    """Two required steps, in order."""
    second_form = Form.objects.create(owner=user, title="Step 2 form")
    process = Process.objects.create(owner=user, title="Linear", type="linear")
    step1 = ProcessStep.objects.create(process=process, form=form, order=0, is_required=True)
    step2 = ProcessStep.objects.create(process=process, form=second_form, order=1, is_required=True)
    return process, step1, step2


@pytest.fixture
def run(linear_process, user):
    process, _, _ = linear_process
    return ProcessRun.objects.create(process=process, respondent=user, session_key="s1")


def _submit(form, run, is_complete=True):
    return Submission.objects.create(form=form, process_run=run, is_complete=is_complete)



@pytest.mark.django_db
def test_assert_step_unlocked_rejects_step_from_another_process(user, form, run):
    other_process = Process.objects.create(owner=user, title="Other", type="free")
    foreign_step = ProcessStep.objects.create(process=other_process, form=form, order=0)

    with pytest.raises(DomainError) as exc:
        assert_step_unlocked(run, foreign_step)
    assert exc.value.code == "step_process_mismatch"


@pytest.mark.django_db
def test_assert_step_unlocked_rejects_completed_run(linear_process, run):
    _, step1, _ = linear_process
    run.status = RunStatus.COMPLETED
    run.save(update_fields=["status"])

    with pytest.raises(DomainError) as exc:
        assert_step_unlocked(run, step1)
    assert exc.value.code == "run_completed"


@pytest.mark.django_db
def test_assert_step_unlocked_free_process_ignores_order(user, form):
    second_form = Form.objects.create(owner=user, title="Free step 2")
    process = Process.objects.create(owner=user, title="Free", type="free")
    ProcessStep.objects.create(process=process, form=form, order=0, is_required=True)
    step2 = ProcessStep.objects.create(process=process, form=second_form, order=1, is_required=True)
    free_run = ProcessRun.objects.create(process=process, respondent=user, session_key="s2")

    assert_step_unlocked(free_run, step2)  


@pytest.mark.django_db
def test_assert_step_unlocked_linear_blocks_until_prior_required_done(linear_process, run):
    _, step1, step2 = linear_process

    with pytest.raises(StepLocked):
        assert_step_unlocked(run, step2)

    submission = _submit(step1.form, run)
    complete_step(run, step1, submission)

    assert_step_unlocked(run, step2)  





@pytest.mark.django_db
def test_complete_step_rejects_wrong_form(linear_process, run):
    _, step1, _ = linear_process
    other_submission = _submit(step1.form, run)
    other_submission.form = Form.objects.create(owner=run.respondent, title="Wrong form")
    other_submission.save(update_fields=["form"])

    with pytest.raises(DomainError) as exc:
        complete_step(run, step1, other_submission)
    assert exc.value.code == "step_form_mismatch"


@pytest.mark.django_db
def test_complete_step_rejects_submission_from_another_run(linear_process, run, user):
    process, step1, _ = linear_process
    other_run = ProcessRun.objects.create(process=process, respondent=user, session_key="s3")
    submission = _submit(step1.form, other_run)

    with pytest.raises(DomainError) as exc:
        complete_step(run, step1, submission)
    assert exc.value.code == "submission_run_mismatch"


@pytest.mark.django_db
def test_complete_step_rejects_incomplete_submission(linear_process, run):
    _, step1, _ = linear_process
    submission = _submit(step1.form, run, is_complete=False)

    with pytest.raises(DomainError) as exc:
        complete_step(run, step1, submission)
    assert exc.value.code == "submission_incomplete"


@pytest.mark.django_db
def test_complete_step_is_idempotent_for_the_same_submission(linear_process, run):
    _, step1, _ = linear_process
    submission = _submit(step1.form, run)

    first = complete_step(run, step1, submission)
    second = complete_step(run, step1, submission)

    assert first.id == second.id
    assert StepCompletion.objects.filter(run=run, step=step1).count() == 1


@pytest.mark.django_db
def test_complete_step_rejects_overwriting_with_different_submission(linear_process, run):
    _, step1, _ = linear_process
    first_submission = _submit(step1.form, run)
    complete_step(run, step1, first_submission)
    second_submission = _submit(step1.form, run)

    with pytest.raises(DomainError) as exc:
        complete_step(run, step1, second_submission)
    assert exc.value.code == "step_already_completed"
    assert exc.value.status_code == 409


@pytest.mark.django_db
def test_run_is_marked_completed_once_all_required_steps_are_done(linear_process, run):
    _, step1, step2 = linear_process

    complete_step(run, step1, _submit(step1.form, run))
    run.refresh_from_db()
    assert run.status == RunStatus.IN_PROGRESS
    assert run.completed_at is None

    complete_step(run, step2, _submit(step2.form, run))
    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED
    assert run.completed_at is not None





@pytest.mark.django_db
def test_next_step_for_run_returns_none_once_completed(linear_process, run):
    run.status = RunStatus.COMPLETED
    run.save(update_fields=["status"])

    assert next_step_for_run(run) is None


@pytest.mark.django_db
def test_next_step_for_run_linear_follows_order(linear_process, run):
    _, step1, step2 = linear_process

    assert next_step_for_run(run) == step1

    complete_step(run, step1, _submit(step1.form, run))
    assert next_step_for_run(run) == step2

    complete_step(run, step2, _submit(step2.form, run))
    assert next_step_for_run(run) is None


@pytest.mark.django_db
def test_next_step_for_run_free_returns_any_uncompleted_step(user, form):
    second_form = Form.objects.create(owner=user, title="Free step 2")
    process = Process.objects.create(owner=user, title="Free", type="free")
    step1 = ProcessStep.objects.create(process=process, form=form, order=0, is_required=True)
    step2 = ProcessStep.objects.create(process=process, form=second_form, order=1, is_required=True)
    free_run = ProcessRun.objects.create(process=process, respondent=user, session_key="s4")

    complete_step(free_run, step2, _submit(step2.form, free_run))

    assert next_step_for_run(free_run) == step1





@pytest.mark.django_db
def test_complete_step_for_submission_ignores_standalone_submissions(user, form):
    submission = Submission.objects.create(form=form, is_complete=True)  # no process_run

    assert complete_step_for_submission(submission) is None


@pytest.mark.django_db
def test_complete_step_for_submission_returns_existing_completion(linear_process, run):
    _, step1, _ = linear_process
    submission = _submit(step1.form, run)
    existing = complete_step(run, step1, submission)

    assert complete_step_for_submission(submission) == existing


@pytest.mark.django_db
def test_complete_step_for_submission_returns_none_when_form_is_not_a_step(linear_process, run, user):
    unrelated_form = Form.objects.create(owner=user, title="Not a step")
    submission = Submission.objects.create(form=unrelated_form, process_run=run, is_complete=True)

    assert complete_step_for_submission(submission) is None


@pytest.mark.django_db
def test_complete_step_for_submission_completes_the_matching_step(linear_process, run):
    _, step1, _ = linear_process
    submission = _submit(step1.form, run)

    completion = complete_step_for_submission(submission)

    assert completion is not None
    assert completion.step_id == step1.id
    assert completion.submission_id == submission.id