from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, db_index=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.username


class OTPPurpose(models.TextChoices):
    REGISTER = "register", "ثبت‌نام"
    LOGIN = "login", "ورود"
    RESET = "reset", "بازیابی رمز"


class OTPRequestLog(TimeStampedModel):
    identifier = models.CharField(max_length=64, db_index=True)
    purpose = models.CharField(max_length=16, choices=OTPPurpose.choices)
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["identifier", "purpose"])]

    def __str__(self) -> str:
        return f"{self.identifier} ({self.purpose})"
