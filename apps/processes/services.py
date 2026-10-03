from django.db import transaction
from django.utils import timezone

from apps.core.cache import invalidate_process
from apps.core.exceptions import DomainError, StepLocked

from .models import ProcessType, ProcessRun, ProcessStep, RunStatus, StepCompletion


def assert_step_unlocked(run: ProcessRun, step: ProcessStep) -> None:
    if run.process_id != step.process_id:
        raise DomainError("این مرحله متعلق به این فرایند نیست.", code="step_process_mismatch")
    if run.status == RunStatus.COMPLETED:
        raise DomainError("این اجرای فرایند قبلاً تکمیل شده است.", code="run_completed")
    if run.process.type == ProcessType.FREE:
        return

    completed_required = set(
        run.completions.filter(step__is_required=True).values_list("step_id", flat=True)
    )
    prior_required = set(
        step.process.steps.filter(is_required=True, order__lt=step.order).values_list("id", flat=True)
    )
    if prior_required - completed_required:
        raise StepLocked("مراحل قبلی اجباری باید تکمیل شوند.")


@transaction.atomic
def complete_step(run: ProcessRun, step: ProcessStep, submission):
    assert_step_unlocked(run, step)
    if run.process_id != step.process_id:
        raise DomainError("این مرحله متعلق به این فرایند نیست.", code="step_process_mismatch")
    if submission.form_id != step.form_id:
        raise DomainError("پاسخ به فرم این مرحله تعلق ندارد.", code="step_form_mismatch")
    if submission.process_run_id != run.id:
        raise DomainError("این پاسخ متعلق به اجرای این فرایند نیست.", code="submission_run_mismatch")
    if not submission.is_complete:
        raise DomainError("پاسخ مرحله هنوز نهایی نشده است.", code="submission_incomplete")

    completion, created = StepCompletion.objects.get_or_create(
        run=run,
        step=step,
        defaults={"submission": submission},
    )
    if not created and completion.submission_id != submission.id:
        raise DomainError(
            "این مرحله قبلاً با پاسخ دیگری تکمیل شده است.",
            code="step_already_completed",
            status_code=409,
        )

    required_ids = set(run.process.steps.filter(is_required=True).values_list("id", flat=True))
    completed_ids = set(
        run.completions.filter(step__is_required=True).values_list("step_id", flat=True)
    )
    if required_ids <= completed_ids and run.status != RunStatus.COMPLETED:
        run.status = RunStatus.COMPLETED
        run.completed_at = timezone.now()
        run.save(update_fields=["status", "completed_at", "updated_at"])
        invalidate_process(run.process_id)
    return completion


def next_step_for_run(run: ProcessRun):
    if run.status == RunStatus.COMPLETED:
        return None
    completed_ids = set(run.completions.values_list("step_id", flat=True))
    steps = run.process.steps.all()
    if run.process.type == ProcessType.FREE:
        return steps.exclude(id__in=completed_ids).first()

    for step in steps.exclude(id__in=completed_ids):
        prior_required = set(
            steps.filter(is_required=True, order__lt=step.order).values_list("id", flat=True)
        )
        if prior_required <= completed_ids:
            return step
    return None


def complete_step_for_submission(submission):
    if not submission.process_run_id:
        return None
    try:
        completion = submission.step_completion
    except StepCompletion.DoesNotExist:
        completion = None
    if completion:
        return completion

    try:
        run = ProcessRun.objects.select_related("process").get(id=submission.process_run_id)
        step = run.process.steps.get(form_id=submission.form_id)
    except (ProcessRun.DoesNotExist, ProcessStep.DoesNotExist):
        return None
    return complete_step(run, step, submission)
