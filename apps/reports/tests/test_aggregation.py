import pytest
from django.utils import timezone

from apps.forms.models import Answer, Field, FieldOption, Submission
from apps.reports.services import aggregate_field


@pytest.mark.django_db
def test_numeric_aggregation(form, user):
    field = Field.objects.create(form=form, type="number", label="Amount")
    for value in [0, 10, 20]:
        submission = Submission.objects.create(form=form, respondent=user, is_complete=True)
        Answer.objects.create(submission=submission, field=field, value=value, value_number=value)
    data = aggregate_field(field)
    assert data["count"] == 3
    assert float(data["avg"]) == 10
    assert float(data["min"]) == 0
    assert float(data["max"]) == 20
    assert float(data["total"]) == 30


@pytest.mark.django_db
def test_distribution_includes_zero_options(form, user):
    field = Field.objects.create(form=form, type="select", label="Choice", config={"multiple": False})
    a = FieldOption.objects.create(field=field, label="A", value="a")
    FieldOption.objects.create(field=field, label="B", value="b")
    submission = Submission.objects.create(form=form, respondent=user, is_complete=True)
    answer = Answer.objects.create(submission=submission, field=field, value="a")
    from apps.forms.models import AnswerOption
    AnswerOption.objects.create(answer=answer, option=a)
    data = aggregate_field(field)
    assert len(data["distribution"]) == 2
    assert sum(item["percent"] for item in data["distribution"]) == 100
    assert next(item for item in data["distribution"] if item["value"] == "b")["count"] == 0


@pytest.mark.django_db
def test_date_timeline_grouped_by_day(form, user):
    field = Field.objects.create(form=form, type="date", label="Date")
    for day in ["2026-10-01", "2026-10-01", "2026-10-02"]:
        submission = Submission.objects.create(form=form, respondent=user, is_complete=True)
        parsed = timezone.datetime.fromisoformat(day).replace(tzinfo=timezone.get_current_timezone())
        Answer.objects.create(submission=submission, field=field, value=day, value_date=parsed)
    data = aggregate_field(field)
    assert {item["count"] for item in data["timeline"]} == {1, 2}



@pytest.mark.django_db
def test_reports_ignore_answers_from_incomplete_submissions(user, form):
    from apps.forms.models import Answer, Field, Submission
    from apps.reports.services import aggregate_field

    field = Field.objects.create(form=form, type="number", label="Score")
    incomplete = Submission.objects.create(form=form, respondent=user, is_complete=False)
    complete = Submission.objects.create(form=form, respondent=user, is_complete=True)
    Answer.objects.create(
        submission=incomplete, field=field, value=10, value_number=10
    )
    Answer.objects.create(
        submission=complete, field=field, value=20, value_number=20
    )

    report = aggregate_field(field)
    assert report["count"] == 1
    assert str(report["total"]) == "20.0000"
