import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.core.exceptions import AccessDenied, DomainError, StepLocked, api_exception_handler


@pytest.mark.parametrize(
  ("exception", "expected_status", "expected_code"),
  [
    (StepLocked("locked"), 409, "step_locked"),
    (AccessDenied("denied"), 403, "access_denied"),
    (DomainError("invalid", code="invalid_value", status_code=422), 422, "invalid_value"),
  ],
)
def test_domain_errors_are_normalized(exception, expected_status, expected_code):
  response = api_exception_handler(exception, {"request": APIRequestFactory().get("/")})

  assert response.status_code == expected_status
  assert response.data["error"]["code"] == expected_code
  assert response.data["error"]["message"]


def test_drf_validation_error_is_normalized():
  response = api_exception_handler(
    ValidationError({"name": ["This field is required."]}),
    {"request": APIRequestFactory().post("/")},
  )

  assert response.status_code == 400
  assert response.data["error"]["code"] == "invalid"
  assert response.data["error"]["detail"]["name"] == ["This field is required."]
