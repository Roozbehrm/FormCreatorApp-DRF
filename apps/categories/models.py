from django.conf import settings
from django.db import models

from apps.core.exceptions import DomainError
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories")
    title = models.CharField(max_length=120)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    color = models.CharField(max_length=7, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "title", "parent"], name="uniq_category_owner_title_parent"
            ),
            models.UniqueConstraint(
                fields=["owner", "title"],
                condition=models.Q(parent__isnull=True),
                name="uniq_category_owner_title_root",
            ),
        ]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.title

    def clean(self):
        node = self.parent
        while node is not None:
            if node.pk == self.pk:
                raise DomainError("حلقه در درخت دسته‌بندی مجاز نیست.", code="category_cycle")
            node = node.parent

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
