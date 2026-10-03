import pytest
from django.core import mail

from apps.accounts import services
from apps.accounts.models import OTPPurpose, OTPRequestLog
from apps.accounts.tasks import send_otp_email, send_otp_sms
from apps.core.exceptions import DomainError


@pytest.mark.django_db
def test_otp_is_one_time(settings, user):
    settings.OTP_LENGTH = 6
    code = services.generate_otp(user.email, OTPPurpose.LOGIN)
    assert services.verify_otp(user.email, OTPPurpose.LOGIN, code) is True
    with pytest.raises(DomainError) as exc_info:
        services.verify_otp(user.email, OTPPurpose.LOGIN, code)
    assert exc_info.value.code == "otp_expired"


@pytest.mark.django_db
def test_wrong_otp_increments_attempts_and_locks(settings, user):
    settings.OTP_MAX_ATTEMPTS = 2
    services.generate_otp(user.email, OTPPurpose.LOGIN)
    with pytest.raises(DomainError) as first:
        services.verify_otp(user.email, OTPPurpose.LOGIN, "000000")
    assert first.value.code == "otp_invalid"
    log = OTPRequestLog.objects.latest("id")
    assert log.attempts == 1
    with pytest.raises(DomainError) as second:
        services.verify_otp(user.email, OTPPurpose.LOGIN, "000000")
    assert second.value.status_code == 429


@pytest.mark.django_db
def test_email_task_writes_message(user):
    send_otp_email(user.email, "123456", OTPPurpose.LOGIN)
    assert len(mail.outbox) == 1
    assert "123456" in mail.outbox[0].body


def test_sms_console_task(settings, capsys):
    settings.SMS_BACKEND = "console"
    send_otp_sms("09120000000", "123456")
    assert "09120000000" in capsys.readouterr().out


@pytest.mark.django_db
def test_otp_rate_limit_blocks_after_window_limit(settings, user):
    settings.OTP_REQUEST_MAX_PER_WINDOW = 2
    services.ensure_otp_rate_limit(user.email)
    services.ensure_otp_rate_limit(user.email)
    with pytest.raises(DomainError) as exc_info:
        services.ensure_otp_rate_limit(user.email)
    assert exc_info.value.code == "otp_throttled"
    assert exc_info.value.status_code == 429


@pytest.mark.django_db
def test_kavenegar_sms_task_uses_verify_lookup_dict(settings):
    settings.SMS_BACKEND = "kavenegar"
    settings.KAVENEGAR_API_KEY = "test-key"
    settings.KAVENEGAR_OTP_TEMPLATE = "verify_otp"

    from unittest.mock import Mock, patch

    client = Mock()
    with patch("kavenegar.KavenegarAPI", return_value=client) as api_cls:
        send_otp_sms("09120000000", "123456")

    api_cls.assert_called_once_with("test-key")
    client.verify_lookup.assert_called_once_with(
        {
            "receptor": "09120000000",
            "template": "verify_otp",
            "token": "123456",
            "type": "sms",
        }
    )


@pytest.mark.django_db
def test_otp_request_endpoint_uses_identifier_rate_limit(api_client, user, settings):
    settings.OTP_REQUEST_MAX_PER_WINDOW = 1
    first = api_client.post(
        "/api/v1/auth/otp/request/",
        {"identifier": user.email, "purpose": OTPPurpose.LOGIN},
        format="json",
    )
    second = api_client.post(
        "/api/v1/auth/otp/request/",
        {"identifier": user.email, "purpose": OTPPurpose.LOGIN},
        format="json",
    )
    assert first.status_code == 202
    assert second.status_code == 429
