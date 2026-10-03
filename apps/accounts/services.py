import hashlib
import secrets

from django.conf import settings
from django.core.cache import cache

from apps.core.exceptions import DomainError

from .models import OTPRequestLog


def normalize_identifier(identifier: str) -> str:
    identifier = identifier.strip()
    return identifier.lower() if "@" in identifier else identifier


def _key(identifier: str, purpose: str) -> str:
    return f"otp:{purpose}:{normalize_identifier(identifier)}"


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _throttle_key(identifier: str) -> str:
    return f"otp:throttle:{normalize_identifier(identifier)}"


def generate_otp(identifier: str, purpose: str, ip: str | None = None) -> str:
    identifier = normalize_identifier(identifier)
    code = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
    cache.set(
        _key(identifier, purpose),
        {"hash": _hash(code), "attempts": 0},
        settings.OTP_TTL_SECONDS,
    )
    OTPRequestLog.objects.create(identifier=identifier, purpose=purpose, ip=ip)
    return code


def verify_otp(identifier: str, purpose: str, code: str) -> bool:
    identifier = normalize_identifier(identifier)
    key = _key(identifier, purpose)
    data = cache.get(key)
    if not data:
        raise DomainError("کد منقضی شده یا وجود ندارد.", code="otp_expired")

    attempts = int(data.get("attempts", 0))
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        raise DomainError("تعداد تلاش بیش از حد مجاز.", code="otp_locked", status_code=429)

    if not secrets.compare_digest(data["hash"], _hash(code)):
        attempts += 1
        data["attempts"] = attempts
        cache.set(key, data, settings.OTP_TTL_SECONDS)
        _update_latest_log(identifier, purpose, attempts=attempts)
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            raise DomainError("تعداد تلاش بیش از حد مجاز.", code="otp_locked", status_code=429)
        raise DomainError("کد نادرست است.", code="otp_invalid")

    cache.delete(key)
    _update_latest_log(identifier, purpose, is_verified=True, attempts=attempts)
    return True


def _update_latest_log(identifier: str, purpose: str, **updates) -> None:
    log = (
        OTPRequestLog.objects.filter(identifier=identifier, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    if log is None:
        return
    for name, value in updates.items():
        setattr(log, name, value)
    log.save(update_fields=[*updates.keys(), "updated_at"])


def ensure_otp_rate_limit(identifier: str) -> None:
    key = _throttle_key(identifier)
    window = getattr(settings, "OTP_REQUEST_WINDOW_SECONDS", 3600)
    limit = getattr(settings, "OTP_REQUEST_MAX_PER_WINDOW", 5)
    count = cache.get(key)
    if count is None:
        cache.add(key, 1, window)
        return
    if int(count) >= limit:
        raise DomainError(
            "تعداد درخواست OTP بیش از حد مجاز است.",
            code="otp_throttled",
            status_code=429,
        )
    cache.incr(key)


def otp_email_subject(purpose: str) -> str:
    labels = {
        "register": "FormFlow registration code",
        "login": "FormFlow login code",
        "reset": "FormFlow password reset code",
    }
    return labels.get(purpose, "FormFlow verification code")


def otp_email_body(code: str, purpose: str = "otp") -> str:
    minutes = max(1, settings.OTP_TTL_SECONDS // 60)
    return f"Your FormFlow verification code is {code}. It expires in {minutes} minutes."
