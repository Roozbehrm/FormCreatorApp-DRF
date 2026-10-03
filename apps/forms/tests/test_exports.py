import csv
from io import BytesIO, StringIO

import pytest
from openpyxl import load_workbook
from rest_framework.test import APIClient

from apps.forms.models import Answer, Field, Submission


@pytest.mark.django_db
def test_submissions_and_exports_include_completed_answers_in_field_order(user, form):
    later_field = Field.objects.create(form=form, type="text", label="Later", order=2)
    first_field = Field.objects.create(form=form, type="text", label="First", order=1)
    completed = Submission.objects.create(form=form, respondent=user, is_complete=True)
    Answer.objects.create(submission=completed, field=later_field, value_text="second")
    Answer.objects.create(submission=completed, field=first_field, value_text="first")
    Submission.objects.create(form=form, respondent=user, is_complete=False)

    client = APIClient()
    client.force_authenticate(user=user)
    base_url = f"/api/v1/forms/{form.uuid}"

    submissions = client.get(f"{base_url}/submissions/")
    csv_response = client.get(f"{base_url}/export/?format=csv")
    xlsx_response = client.get(f"{base_url}/export/?format=xlsx")

    assert submissions.status_code == 200
    assert submissions.data["count"] == 1
    assert [answer["value"] for answer in submissions.data["results"][0]["answers"]] == ["first", "second"]

    csv_rows = list(csv.reader(StringIO(csv_response.content.decode("utf-8-sig"))))
    assert csv_response.status_code == 200
    assert csv_rows == [["submission_id", "submitted_at", "First", "Later"], [str(completed.id), "", "first", "second"]]

    workbook = load_workbook(BytesIO(xlsx_response.content), read_only=True)
    assert xlsx_response.status_code == 200
    assert list(workbook.active.values) == [
        ("submission_id", "submitted_at", "First", "Later"),
        (completed.id, None, "first", "second"),
    ]
