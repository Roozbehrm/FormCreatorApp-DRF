import uuid as uuid_lib

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    uuid = models.UUIDField(default=uuid_lib.uuid4, unique=True, editable=False, db_index=True)

    class Meta:
        abstract = True


class Visibility(models.TextChoices):
    PUBLIC = "public", "عمومی"
    PRIVATE = "private", "خصوصی"


class ShareableModel(TimeStampedModel, UUIDModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC)
    access_password = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def is_private(self) -> bool:
        return self.visibility == Visibility.PRIVATE

    def set_access_password(self, raw_password: str) -> None:
        from django.contrib.auth.hashers import make_password

        self.access_password = make_password(raw_password) if raw_password else ""

    def check_access_password(self, raw_password: str) -> bool:
        from django.contrib.auth.hashers import check_password

        if not self.access_password:
            return False
        return check_password(raw_password, self.access_password)
