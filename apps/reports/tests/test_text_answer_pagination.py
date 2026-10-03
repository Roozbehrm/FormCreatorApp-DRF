import pytest

from apps.forms.models import Answer, Field, Submission
from apps.reports.services import text_answer_page


@pytest.mark.django_db
def test_text_answers_are_paginated(form, user):
    field = Field.objects.create(form=form, type="text", label="Response")
    for index in range(25):
        submission = Submission.objects.create(form=form, respondent=user, is_complete=True)
        Answer.objects.create(submission=submission, field=field, value_text=f"answer-{index}")

    first_page = text_answer_page(field, page="1", page_size="10")
    second_page = text_answer_page(field, page="2", page_size="10")

    first_values = {answer["value"] for answer in first_page["results"]}
    second_values = {answer["value"] for answer in second_page["results"]}
    assert first_page["count"] == 25
    assert first_page["total_pages"] == 3
    assert first_page["page"] == 1
    assert second_page["page"] == 2
    assert len(first_values) == len(second_values) == 10
    assert first_values.isdisjoint(second_values)
