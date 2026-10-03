import pytest
from django.core.cache import cache

from apps.forms.models import Field, Form, Submission
from apps.reports.models import TargetType, VisitCounter
from apps.reports.services import form_report, record_visit
from apps.reports.tasks import flush_visit_counters


@pytest.fixture
def another_form(user):
    return Form.objects.create(owner=user, title="Another form")


@pytest.mark.django_db
def test_visit_record_and_flush(form):
    cache.clear()
    assert record_visit(TargetType.FORM, form.id) == 1
    assert record_visit(TargetType.FORM, form.id) == 2
    flushed = flush_visit_counters()
    assert flushed == 2
    assert VisitCounter.objects.get(target_type="form", object_id=form.id).count == 2


@pytest.mark.django_db
def test_form_report_cache_invalidates_after_answer(settings, form, user):
    settings.CACHE_TTL_REPORT = 300
    Field.objects.create(form=form, type="text", label="Name")
    first = form_report(form)
    assert first["submissions"] == 0
    Submission.objects.create(form=form, respondent=user, is_complete=True)
    from apps.core.cache import invalidate_form
    invalidate_form(form.id, form.uuid)
    second = form_report(form)
    assert second["submissions"] == 1


@pytest.mark.django_db
def test_process_report_cache_invalidates_when_nested_form_changes(user, form, another_form):
    from apps.processes.models import Process, ProcessStep
    from apps.reports.services import process_report

    process = Process.objects.create(owner=user, title="Process")
    ProcessStep.objects.create(process=process, form=form, order=1, is_required=True)
    ProcessStep.objects.create(process=process, form=another_form, order=2, is_required=False)

    first = process_report(process)
    assert first["steps"][0]["submissions"] == 0

    Submission.objects.create(form=form, respondent=user, is_complete=True)
    second = process_report(process)
    assert second["steps"][0]["submissions"] == 1
