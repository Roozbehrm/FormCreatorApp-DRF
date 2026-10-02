import pytest

from apps.accounts import services
from apps.core.exceptions import DomainError


@pytest.mark.django_db
def test_otp_correct_code_verified():
    code = services.generate_otp("test@example.com", "login")
    assert services.verify_otp("test@example.com", "login", code) is True


@pytest.mark.django_db
def test_otp_wrong_code_raises():
    services.generate_otp("test2@example.com", "login")
    with pytest.raises(DomainError):
        services.verify_otp("test2@example.com", "login", "000000")


@pytest.mark.django_db
def test_otp_expired_raises():
    with pytest.raises(DomainError):
        services.verify_otp("never-requested@example.com", "login", "123456")


@pytest.mark.django_db
def test_otp_locked_after_max_attempts(settings):
    settings.OTP_MAX_ATTEMPTS = 2
    services.generate_otp("test3@example.com", "login")
    for _ in range(2):
        try:
            services.verify_otp("test3@example.com", "login", "000000")
        except DomainError:
            pass
    with pytest.raises(DomainError) as exc_info:
        services.verify_otp("test3@example.com", "login", "000000")
    assert exc_info.value.status_code == 429
