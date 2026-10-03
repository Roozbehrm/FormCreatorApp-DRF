import pytest

from apps.core.exceptions import DomainError, StepLocked
from apps.forms.models import Field
from apps.forms.services import finalize_submission, start_submission, submit_field_answer


@pytest.mark.django_db
def test_ordered_form_locks_next_field(user, form):
    form.enforce_field_order = True
    form.save(update_fields=["enforce_field_order"])
    first = Field.objects.create(form=form, type="text", label="First", order=1)
    second = Field.objects.create(form=form, type="text", label="Second", order=2)
    submission = start_submission(form=form, respondent=user, session_key="abc")
    with pytest.raises(StepLocked):
        submit_field_answer(submission=submission, field=second, raw="two")
    submit_field_answer(submission=submission, field=first, raw="one")
    assert submission.answers.filter(field=first).exists()


@pytest.mark.django_db
def test_unordered_form_saves_incrementally(user, form):
    first = Field.objects.create(form=form, type="text", label="First", is_required=True)
    second = Field.objects.create(form=form, type="text", label="Second")
    submission = start_submission(form=form, respondent=user, session_key="abc")
    submit_field_answer(submission=submission, field=second, raw="two")
    assert submission.answers.filter(field=second).exists()
    with pytest.raises(DomainError):
        finalize_submission(submission)
    submit_field_answer(submission=submission, field=first, raw="one")
    finalize_submission(submission)
    submission.refresh_from_db()
    assert submission.is_complete is True


@pytest.mark.django_db
def test_required_empty_is_rejected(user, form):
    field = Field.objects.create(form=form, type="text", label="Required", is_required=True)
    submission = start_submission(form=form, respondent=user)
    with pytest.raises(DomainError):
        submit_field_answer(submission=submission, field=field, raw="")
