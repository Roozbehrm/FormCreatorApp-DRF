import hmac

from django.conf import settings
from django.core import signing
from django.core.signing import BadSignature

from .exceptions import AccessDenied

ACCESS_TOKEN_HEADER = "X-Private-Access-Token"
SESSION_KEY_HEADER = "X-Session-Key"


def make_access_token(resource_type: str, object_id: int) -> str:
    return signing.dumps(
        {"resource_type": resource_type, "object_id": int(object_id)},
        salt=settings.PRIVATE_ACCESS_TOKEN_SALT,
        compress=True,
    )


def has_valid_access(resource_type: str, object_id: int, request) -> bool:
    token = request.headers.get(ACCESS_TOKEN_HEADER, "")
    if not token:
        return False
    try:
        payload = signing.loads(
            token,
            salt=settings.PRIVATE_ACCESS_TOKEN_SALT,
            max_age=settings.PRIVATE_ACCESS_TOKEN_TTL_SECONDS,
        )
    except BadSignature:
        return False
    return payload == {"resource_type": resource_type, "object_id": int(object_id)}


def assert_private_access(resource, request, resource_type: str) -> None:
    if not resource.is_private:
        return

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and resource.owner_id == user.pk:
        return

    if not has_valid_access(resource_type, resource.pk, request):
        raise AccessDenied("برای دسترسی به این مورد باید ابتدا گذرواژه را وارد کنید.")


def assert_owns(resource, request) -> None:
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        if getattr(resource, "owner_id", None) == user.pk:
            return
        if getattr(resource, "respondent_id", None) == user.pk:
            return

    request_session_key = request.headers.get(SESSION_KEY_HEADER, "")
    data = getattr(request, "data", {})
    if not request_session_key and isinstance(data, dict):
        request_session_key = data.get("session_key", "")
    resource_session_key = getattr(resource, "session_key", "")
    if request_session_key and resource_session_key and hmac.compare_digest(
        str(request_session_key), str(resource_session_key)
    ):
        return

    raise AccessDenied("اجازه‌ی دسترسی به این مورد را ندارید.")

def get_guest_session_key(request) -> str:
    """
    Return the guest session key associated with the request.

    An existing X-Session-Key is accepted for resuming a guest session.
    When no key is supplied, use Django's session key and create the
    session when necessary.
    """
    session_key = request.headers.get(SESSION_KEY_HEADER)

    if session_key:
        if not isinstance(session_key, str):
            raise ValueError("Session key must be a string.")

        session_key = session_key.strip()

        if not session_key:
            raise ValueError("Session key cannot be empty.")

        if len(session_key) > 64:
            raise ValueError("Session key is too long.")

        return session_key

    session = getattr(request, "session", None)

    if session is not None:
        if not session.session_key:
            session.create()

        if session.session_key:
            return session.session_key

    # Fallback for lightweight RequestFactory-style requests.
    from secrets import token_urlsafe

    return token_urlsafe(32)