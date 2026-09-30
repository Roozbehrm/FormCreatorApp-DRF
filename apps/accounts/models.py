"""
مالک: روزبه (تسک #1 — feature/1-accounts-models)
مهیار این فایل و migrationها را تغییر نمی‌دهد؛ نیاز به فیلد/مدل جدید را به روزبه بگوید.
TODO:
  - User(AbstractUser)         phone (unique, nullable), email (unique), is_verified
        USERNAME_FIELD = "username", REQUIRED_FIELDS = ["email"]
  - OTPPurpose(TextChoices)    register | login | reset
  - OTPRequestLog(TimeStampedModel)
        identifier, purpose, is_verified, attempts, ip
        (فقط برای audit — خود کد OTP در Redis نگهداری می‌شود، نه اینجا)

پیش‌نیاز: تسک #3 — apps/core/models.py (TimeStampedModel) باید قبلش تمام شده باشد.
"""
