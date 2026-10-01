from django.conf import settings
from django.db import models

from apps.core.models import ShareableModel, TimeStampedModel


class ProcessType(models.TextChoices):
    LINEAR = "linear", "خطی (پیش‌نیازدار)"
    FREE = "free", "آزاد"


class Process(ShareableModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="processes")
    category = models.ForeignKey(
        "categories.Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="processes"
    )
    type = models.CharField(max_length=10, choices=ProcessType.choices, default=ProcessType.LINEAR)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class ProcessStep(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="steps")
    form = models.ForeignKey("forms.Form", on_delete=models.PROTECT, related_name="process_steps")
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")
        unique_together = ("process", "form")


class RunStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "در حال انجام"
    COMPLETED = "completed", "تکمیل‌شده"


class ProcessRun(TimeStampedModel):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="runs")
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="process_runs"
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(max_length=12, choices=RunStatus.choices, default=RunStatus.IN_PROGRESS)
    completed_at = models.DateTimeField(null=True, blank=True)


class StepCompletion(models.Model):
    run = models.ForeignKey(ProcessRun, on_delete=models.CASCADE, related_name="completions")
    step = models.ForeignKey(ProcessStep, on_delete=models.CASCADE, related_name="completions")
    submission = models.OneToOneField("forms.Submission", on_delete=models.CASCADE, related_name="step_completion")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("run", "step")
