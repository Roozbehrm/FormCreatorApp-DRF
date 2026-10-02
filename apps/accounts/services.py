import hashlib
import secrets

from django.conf import settings
from django.core.cache import cache

from apps.core.exceptions import DomainError

from .models import OTPRequestLog


def _key(identifier: str, purpose: str) -> str:
    return f"otp:{purpose}:{identifier}"


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_otp(identifier: str, purpose: str, ip: str | None = None) -> str:
    code = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
    cache.set(_key(identifier, purpose), {"hash": _hash(code), "attempts": 0}, settings.OTP_TTL_SECONDS)
    OTPRequestLog.objects.create(identifier=identifier, purpose=purpose, ip=ip)
    return code


def verify_otp(identifier: str, purpose: str, code: str) -> bool:
    data = cache.get(_key(identifier, purpose))
    if not data:
        raise DomainError("کد منقضی شده یا وجود ندارد.", code="otp_expired")
    if data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
        raise DomainError("تعداد تلاش بیش از حد مجاز.", code="otp_locked", status_code=429)
    if data["hash"] != _hash(code):
        data["attempts"] += 1
        cache.set(_key(identifier, purpose), data, settings.OTP_TTL_SECONDS)
        raise DomainError("کد نادرست است.", code="otp_invalid")
    cache.delete(_key(identifier, purpose))
    log = OTPRequestLog.objects.filter(identifier=identifier, purpose=purpose).order_by("-created_at").first()
    if log:
        log.is_verified = True
        log.save(update_fields=["is_verified"])
    return True
