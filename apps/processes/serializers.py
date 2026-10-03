from django.db import transaction
from rest_framework import serializers

from .models import Process, ProcessRun, ProcessStep, StepCompletion


class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ("id", "process", "form", "order", "is_required")
        read_only_fields = ("id", "process")

    def validate_form(self, value):
        request = self.context["request"]
        process = self.context.get("process")
        if process and value.owner_id != process.owner_id:
            raise serializers.ValidationError("فرم باید متعلق به مالک فرایند باشد.")
        if value.owner_id != request.user.id:
            raise serializers.ValidationError("فقط فرم‌های خودتان را می‌توانید انتخاب کنید.")
        return value


class ProcessSerializer(serializers.ModelSerializer):
    steps = ProcessStepSerializer(many=True, required=False)

    class Meta:
        model = Process
        fields = (
            "id",
            "uuid",
            "owner",
            "category",
            "title",
            "description",
            "visibility",
            "access_password",
            "is_active",
            "type",
            "steps",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "uuid", "owner", "created_at", "updated_at")
        extra_kwargs = {"access_password": {"write_only": True, "required": False}}

    def validate_category(self, value):
        request = self.context["request"]
        if value and value.owner_id != request.user.id:
            raise serializers.ValidationError("دسته باید متعلق به خودتان باشد.")
        return value

    def validate(self, attrs):
        visibility = attrs.get("visibility", getattr(self.instance, "visibility", "public"))
        password = attrs.get("access_password")
        current_password = getattr(self.instance, "access_password", "")
        if visibility == "private" and not password and not current_password:
            raise serializers.ValidationError({"access_password": "فرایند خصوصی باید گذرواژه داشته باشد."})
        if "access_password" in attrs and visibility == "private" and not password:
            raise serializers.ValidationError({"access_password": "گذرواژه‌ی فرایند خصوصی نمی‌تواند خالی باشد."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        steps_data = validated_data.pop("steps", [])
        password = validated_data.pop("access_password", "")
        process = Process.objects.create(owner=self.context["request"].user, **validated_data)
        if process.is_private and password:
            process.set_access_password(password)
            process.save(update_fields=["access_password"])
        step_serializer = ProcessStepSerializer(context={**self.context, "process": process})
        for idx, item in enumerate(steps_data):
            item.setdefault("order", idx)
            step_serializer.create({**item, "process": process})
        return process

    @transaction.atomic
    def update(self, instance, validated_data):
        steps_data = validated_data.pop("steps", None)
        password = validated_data.pop("access_password", None)
        process = super().update(instance, validated_data)
        if password is not None:
            process.set_access_password(password)
            process.save(update_fields=["access_password"])
        if steps_data is not None:
            process.steps.all().delete()
            step_serializer = ProcessStepSerializer(context={**self.context, "process": process})
            for idx, item in enumerate(steps_data):
                item.setdefault("order", idx)
                step_serializer.create({**item, "process": process})
        return process


class ProcessRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRun
        fields = (
            "id",
            "process",
            "respondent",
            "session_key",
            "status",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PublicProcessRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRun
        fields = ("id", "status", "completed_at", "created_at", "updated_at")
        read_only_fields = fields


class StepCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepCompletion
        fields = ("id", "run", "step", "submission", "completed_at")
        read_only_fields = fields


class PublicProcessStepSerializer(serializers.ModelSerializer):
    form_uuid = serializers.UUIDField(source="form.uuid", read_only=True)
    form_title = serializers.CharField(source="form.title", read_only=True)

    class Meta:
        model = ProcessStep
        fields = ("id", "form_uuid", "form_title", "order", "is_required")


class PublicProcessSerializer(serializers.ModelSerializer):
    steps = PublicProcessStepSerializer(many=True, read_only=True)

    class Meta:
        model = Process
        fields = ("uuid", "title", "description", "visibility", "type", "steps")


class PublicProcessStateSerializer(serializers.Serializer):
    process = PublicProcessSerializer()
    run = PublicProcessRunSerializer()
    completed_step_ids = serializers.ListField(child=serializers.IntegerField())
    next_step_id = serializers.IntegerField(allow_null=True)
    session_key = serializers.CharField()
