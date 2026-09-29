"""
مالک: مهیار
TODO:
  - User(AbstractUser)         phone (unique, nullable), email (unique), is_verified
        USERNAME_FIELD = "username", REQUIRED_FIELDS = ["email"]
  - OTPPurpose(TextChoices)    register | login | reset
  - OTPRequestLog(TimeStampedModel)
        identifier, purpose, is_verified, attempts, ip
        (فقط برای audit — خود کد OTP در Redis نگهداری می‌شود، نه اینجا)

پیش‌نیاز: apps/core/models.py (TimeStampedModel) باید قبلش تمام شده باشد.
"""
