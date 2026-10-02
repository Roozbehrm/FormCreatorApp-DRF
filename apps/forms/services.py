from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.cache import invalidate_form
from apps.core.exceptions import AccessDenied, DomainError, StepLocked

from .fields.base import FieldRegistry
from .models import Answer, AnswerOption, Form, Submission


def unlock_form(form: Form, password: str) -> None:
    """اگر فرم خصوصی است، گذرواژه را چک می‌کند؛ در غیر این صورت خطای دسترسی می‌دهد."""
    if not form.is_private:
        return
    if not form.check_access_password(password):
        raise AccessDenied("گذرواژه‌ی فرم نادرست است.")


def start_submission(*, form: Form, respondent=None, session_key: str = "", ip=None, process_run=None) -> Submission:
    if not form.is_accepting_responses():
        raise DomainError("این فرم دیگر پاسخ نمی‌پذیرد.", code="form_closed")
    return Submission.objects.create(
        form=form, respondent=respondent, session_key=session_key, ip=ip, process_run=process_run
    )


def assert_field_unlocked(submission: Submission, field) -> None:
    if not submission.form.enforce_field_order:
        return
    previous_ids = set(
        submission.form.fields.filter(
            Q(order__lt=field.order) | Q(order=field.order, id__lt=field.id)
        ).values_list("id", flat=True)
    )
    answered_ids = set(submission.answers.values_list("field_id", flat=True))
    if previous_ids - answered_ids:
        raise StepLocked("برای این سوال باید ابتدا سوالات قبلی را جواب دهید.")


@transaction.atomic
def submit_field_answer(*, submission: Submission, field, raw) -> Answer:
    if field.form_id != submission.form_id:
        raise DomainError("این سوال متعلق به این فرم نیست.", code="field_form_mismatch")
    assert_field_unlocked(submission, field)

    if raw in (None, "", []):
        if field.is_required:
            raise DomainError(f"«{field.label}» اجباری است.", code="required")
        Answer.objects.filter(submission=submission, field=field).delete()
        return None

    parsed = FieldRegistry.get(field.type).validate_answer(field, raw)
    answer, _ = Answer.objects.update_or_create(
        submission=submission,
        field=field,
        defaults={
            "value": parsed.value,
            "value_number": parsed.value_number,
            "value_date": parsed.value_date,
            "value_text": parsed.value_text,
        },
    )
    answer.selected_options.all().delete()
    if parsed.option_values:
        options = field.options.filter(value__in=parsed.option_values)
        AnswerOption.objects.bulk_create([AnswerOption(answer=answer, option=o) for o in options])
    return answer


def finalize_submission(submission: Submission) -> Submission:
    required_ids = set(submission.form.fields.filter(is_required=True).values_list("id", flat=True))
    answered_ids = set(submission.answers.values_list("field_id", flat=True))
    missing = required_ids - answered_ids
    if missing:
        raise DomainError("همه‌ی سوالات اجباری جواب داده نشده‌اند.", code="incomplete_submission")
    submission.is_complete = True
    submission.completed_at = timezone.now()
    submission.save(update_fields=["is_complete", "completed_at"])
    invalidate_form(submission.form_id, submission.form.uuid)
    return submission


@transaction.atomic
def submit_form(*, form: Form, data: dict, respondent=None, session_key: str = "", ip=None, process_run=None) -> Submission:

    submission = start_submission(
        form=form, respondent=respondent, session_key=session_key, ip=ip, process_run=process_run
    )
    for field in form.fields.all():
        raw = data.get(str(field.id))
        submit_field_answer(submission=submission, field=field, raw=raw)
    finalize_submission(submission)
    return submission
