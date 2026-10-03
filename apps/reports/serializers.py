from rest_framework import serializers

from apps.forms.models import Form
from apps.processes.models import Process

from .models import Delivery, ReportSchedule, TargetType


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = (
            "id",
            "owner",
            "target_type",
            "object_id",
            "period",
            "delivery",
            "email",
            "webhook_url",
            "secret",
            "last_run_at",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "last_run_at", "created_at", "updated_at")
        extra_kwargs = {"secret": {"write_only": True, "required": False}}

    def validate(self, attrs):
        instance = self.instance
        target_type = attrs.get("target_type", getattr(instance, "target_type", ""))
        object_id = attrs.get("object_id", getattr(instance, "object_id", None))
        delivery = attrs.get("delivery", getattr(instance, "delivery", Delivery.EMAIL))
        webhook_url = attrs.get("webhook_url", getattr(instance, "webhook_url", ""))
        secret = attrs.get("secret", getattr(instance, "secret", ""))
        owner = self.context["request"].user

        if not target_type or object_id is None:
            raise serializers.ValidationError(
                {"target_type": "گزارش باید target_type و object_id داشته باشد."}
            )

        model = {
            TargetType.FORM: Form,
            TargetType.PROCESS: Process,
        }.get(target_type)
        if model is None or not model.objects.filter(id=object_id, owner=owner).exists():
            raise serializers.ValidationError({"object_id": "این منبع متعلق به شما نیست."})

        if delivery == Delivery.EMAIL:
            if webhook_url:
                raise serializers.ValidationError(
                    {"webhook_url": "در ارسال ایمیلی webhook تنظیم نکنید."}
                )
        elif delivery == Delivery.WEBHOOK:
            errors = {}
            if not webhook_url:
                errors["webhook_url"] = "برای webhook لازم است."
            if not secret:
                errors["secret"] = "برای webhook secret لازم است."
            if errors:
                raise serializers.ValidationError(errors)

        return attrs
