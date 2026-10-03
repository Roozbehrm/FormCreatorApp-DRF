from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .services import otp_email_body, otp_email_subject


@shared_task
def send_otp_email(email: str, code: str, purpose: str = "otp") -> None:
    send_mail(
        subject=otp_email_subject(purpose),
        message=otp_email_body(code, purpose),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_otp_sms(phone: str, code: str) -> None:
    backend = settings.SMS_BACKEND
    if backend == "console":
        print(f"[SMS-STUB] to={phone} code={code}")
        return
    if backend != "kavenegar":
        raise RuntimeError(f"Unsupported SMS_BACKEND: {backend}")

    from kavenegar import KavenegarAPI

    if not settings.KAVENEGAR_API_KEY or not settings.KAVENEGAR_OTP_TEMPLATE:
        raise RuntimeError("KAVENEGAR_API_KEY and KAVENEGAR_OTP_TEMPLATE are required")

    client = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    client.verify_lookup(
        {
            "receptor": phone,
            "template": settings.KAVENEGAR_OTP_TEMPLATE,
            "token": code,
            "type": "sms",
        }
    )
