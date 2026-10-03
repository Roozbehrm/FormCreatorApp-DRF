from django.conf import settings
from django.db import models

from apps.core.models import ShareableModel, TimeStampedModel


class FieldType(models.TextChoices):
    TEXT = "text", "متن کوتاه"
    TEXTAREA = "textarea", "متن بلند"
    NUMBER = "number", "عدد"
    SELECT = "select", "انتخابی"
    CHECKBOX = "checkbox", "چندانتخابی"
    RATING = "rating", "امتیاز"
    DATE = "date", "تاریخ"


class Form(ShareableModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forms")
    category = models.ForeignKey(
        "categories.Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="forms"
    )
    accepts_responses_until = models.DateTimeField(null=True, blank=True)
    enforce_field_order = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title

    def is_accepting_responses(self) -> bool:
        if not self.is_active:
            return False
        if self.accepts_responses_until:
            from django.utils import timezone

            return timezone.now() <= self.accepts_responses_until
        return True


class Field(TimeStampedModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    type = models.CharField(max_length=16, choices=FieldType.choices)
    label = models.CharField(max_length=255)
    help_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("order", "id")
        indexes = [models.Index(fields=["form", "order"])]

    def __str__(self) -> str:
        return f"{self.form_id}:{self.label}"


class FieldOption(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")
        unique_together = ("field", "value")

    def __str__(self) -> str:
        return self.label


class Submission(TimeStampedModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    process_run = models.ForeignKey(
        "processes.ProcessRun", null=True, blank=True, on_delete=models.CASCADE, related_name="submissions"
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="submissions"
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["form", "created_at"])]

    def __str__(self) -> str:
        return f"submission#{self.pk} form={self.form_id}"


class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="answers")
    value = models.JSONField(null=True, blank=True)
    value_number = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, db_index=True)
    value_date = models.DateTimeField(null=True, blank=True, db_index=True)
    value_text = models.TextField(blank=True)

    class Meta:
        unique_together = ("submission", "field")
        indexes = [models.Index(fields=["field", "value_number"])]


class AnswerOption(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="selected_options")
    option = models.ForeignKey(FieldOption, on_delete=models.CASCADE, related_name="answer_links")

    class Meta:
        unique_together = ("answer", "option")
