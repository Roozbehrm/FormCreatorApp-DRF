from types import SimpleNamespace

import pytest
from django.test import RequestFactory

from apps.core.access import assert_owns, assert_private_access, make_access_token
from apps.core.exceptions import AccessDenied


def _request(*, token="", session_key="", user=None):
    request = RequestFactory().get(
        "/",
        HTTP_X_PRIVATE_ACCESS_TOKEN=token,
        HTTP_X_SESSION_KEY=session_key,
    )
    request.user = user or SimpleNamespace(is_authenticated=False)
    request.data = {}
    return request


def test_private_access_accepts_matching_signed_token():
    resource = SimpleNamespace(pk=7, owner_id=2, is_private=True)
    request = _request(token=make_access_token("form", resource.pk))

    assert_private_access(resource, request, "form")


def test_private_access_rejects_wrong_resource_or_invalid_token():
    resource = SimpleNamespace(pk=7, owner_id=2, is_private=True)

    with pytest.raises(AccessDenied):
        assert_private_access(resource, _request(token=make_access_token("process", 7)), "form")
    with pytest.raises(AccessDenied):
        assert_private_access(resource, _request(token="not-a-signed-token"), "form")


def test_private_access_allows_owner_without_unlock_token():
    owner = SimpleNamespace(pk=2, is_authenticated=True)
    resource = SimpleNamespace(pk=7, owner_id=2, is_private=True)

    assert_private_access(resource, _request(user=owner), "form")


def test_assert_owns_accepts_matching_guest_session_only():
    resource = SimpleNamespace(owner_id=None, respondent_id=None, session_key="guest-session")

    assert_owns(resource, _request(session_key="guest-session"))
    with pytest.raises(AccessDenied):
        assert_owns(resource, _request(session_key="other-session"))
