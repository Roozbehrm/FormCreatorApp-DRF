import json

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_graphql_form_report_requires_owner_jwt_cookie(user, form):
    client = APIClient()
    login = client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "StrongPass123!"},
        format="json",
    )
    assert login.status_code == 200

    response = client.post(
        "/graphql/",
        {"query": f'query {{ formReport(uuid: "{form.uuid}") }}'},
        format="json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )

    assert response.status_code == 200
    payload = json.loads(response.content)
    assert payload["data"]["formReport"]["form_id"] == form.id
