"""
مالک: مهیار
TODO:
  - generate_otp(identifier: str, purpose: str) -> str
        تولید کد، هش‌کردن، ذخیره در Redis با TTL (settings.OTP_TTL_SECONDS)
  - verify_otp(identifier: str, purpose: str, code: str) -> bool
        بررسی هش، سقف تلاش (settings.OTP_MAX_ATTEMPTS)، انقضا
        خطاها از طریق apps.core.exceptions.DomainError
"""
