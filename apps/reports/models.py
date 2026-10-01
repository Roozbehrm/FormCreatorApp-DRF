from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class TargetType(models.TextChoices):
    FORM = "form", "فرم"
    PROCESS = "process", "فرایند"


class VisitCounter(models.Model):
    target_type = models.CharField(max_length=10, choices=TargetType.choices)
    object_id = models.PositiveIntegerField()
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("target_type", "object_id", "date")
        indexes = [models.Index(fields=["target_type", "object_id"])]


class Period(models.TextChoices):
    WEEKLY = "weekly", "هفتگی"
    MONTHLY = "monthly", "ماهانه"


class Delivery(models.TextChoices):
    EMAIL = "email", "ایمیل"
    WEBHOOK = "webhook", "ارسال به API"


class ReportSchedule(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_schedules")
    target_type = models.CharField(max_length=10, choices=TargetType.choices, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    period = models.CharField(max_length=10, choices=Period.choices, default=Period.WEEKLY)
    delivery = models.CharField(max_length=10, choices=Delivery.choices, default=Delivery.EMAIL)
    email = models.EmailField(blank=True)
    webhook_url = models.URLField(blank=True)
    secret = models.CharField(max_length=128, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_due(self, now) -> bool:
        if not self.is_active:
            return False
        if self.last_run_at is None:
            return True
        delta = now - self.last_run_at
        days = 7 if self.period == Period.WEEKLY else 30
        return delta.days >= days


class ReportDelivery(TimeStampedModel):
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.CASCADE, related_name="deliveries")
    is_success = models.BooleanField(default=False)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    error = models.TextField(blank=True)
