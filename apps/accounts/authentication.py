from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

ACCESS_TOKEN_COOKIE = "access"
REFRESH_TOKEN_COOKIE = "refresh"


def enforce_csrf(request):
    SessionAuthentication().enforce_csrf(request)


def set_auth_cookies(response, tokens, request):
    get_token(request)
    cookie_options = {
        "httponly": True,
        "secure": settings.SESSION_COOKIE_SECURE,
        "samesite": settings.SESSION_COOKIE_SAMESITE,
        "path": "/",
    }
    if "access" in tokens:
        response.set_cookie(
            ACCESS_TOKEN_COOKIE,
            tokens["access"],
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            **cookie_options,
        )
    if "refresh" in tokens:
        response.set_cookie(
            REFRESH_TOKEN_COOKIE,
            tokens["refresh"],
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            **cookie_options,
        )


def clear_auth_cookies(response):
    for cookie_name in (ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE):
        response.delete_cookie(cookie_name, path="/", samesite=settings.SESSION_COOKIE_SAMESITE)


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if self.get_header(request) is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token