from rest_framework import serializers

from apps.forms.fields.base import FieldRegistry
from apps.forms.models import Field, FieldOption, Form


class FieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOption
        fields = ["id", "label", "value", "order"]
        read_only_fields = ["id"]


class FieldReorderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    order = serializers.IntegerField(min_value=0)


class FieldBulkReorderSerializer(serializers.Serializer):
    fields = FieldReorderItemSerializer(many=True, allow_empty=False)

    def validate_fields(self, fields):
        field_ids = [item["id"] for item in fields]

        if len(field_ids) != len(set(field_ids)):
            raise serializers.ValidationError("شناسه‌ی هر فیلد باید یکتا باشد.")

        return fields


class FieldSerializer(serializers.ModelSerializer):
    options = FieldOptionSerializer(many=True, required=False)

    class Meta:
        model = Field
        fields = [
            "id",
            "form",
            "type",
            "label",
            "help_text",
            "order",
            "is_required",
            "config",
            "options",
        ]
        read_only_fields = ["id", "form"]

    def validate_config(self, config):
        field_type = self.initial_data.get("type")

        if not field_type and self.instance:
            field_type = self.instance.type

        handler = FieldRegistry.get(field_type)
        return handler.validate_config(config)

    def validate(self, attrs):
        field_type = attrs.get("type")

        if not field_type and self.instance:
            field_type = self.instance.type

        handler = FieldRegistry.get(field_type)

        if self.instance and self.instance.form.submissions.filter(is_complete=True).exists():
            protected = {"type", "label", "help_text", "is_required", "config", "options"}
            changed = protected.intersection(attrs)
            if changed:
                raise serializers.ValidationError(
                    {"field": "ساختار فیلد پس از ثبت پاسخ قابل تغییر نیست."}
                )

        options = attrs.get("options")

        if handler.requires_options and not options and not self.instance:
            raise serializers.ValidationError({"options": "برای این نوع فیلد باید گزینه تعریف شود."})

        return attrs

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        field = super().create(validated_data)

        for option_data in options_data:
            FieldOption.objects.create(
                field=field,
                **option_data,
            )

        return field

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)

        instance = super().update(instance, validated_data)

        if options_data is not None:
            instance.options.all().delete()

            for option_data in options_data:
                FieldOption.objects.create(
                    field=instance,
                    **option_data,
                )

        return instance


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            "uuid",
            "title",
            "description",
            "visibility",
            "access_password",
            "is_active",
            "owner",
            "category",
            "accepts_responses_until",
            "enforce_field_order",
        ]
        read_only_fields = ["uuid", "owner"]
        extra_kwargs = {
            "access_password": {"write_only": True},
        }

    def create(self, validated_data):
        raw_password = validated_data.pop("access_password", "")

        form = Form(
            owner=self.context["request"].user,
            **validated_data,
        )

        if raw_password:
            form.set_access_password(raw_password)

        form.save()
        return form

    def update(self, instance, validated_data):
        raw_password = validated_data.pop("access_password", None)

        instance = super().update(instance, validated_data)

        if raw_password is not None:
            instance.set_access_password(raw_password)
            instance.save(update_fields=["access_password", "updated_at"])

        return instance


class FormDetailSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = [
            "uuid",
            "title",
            "description",
            "visibility",
            "is_active",
            "category",
            "accepts_responses_until",
            "enforce_field_order",
            "fields",
        ]
        read_only_fields = ["uuid"]


class PublicFieldSerializer(serializers.ModelSerializer):
    options = FieldOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Field
        fields = ("id", "type", "label", "help_text", "order", "is_required", "config", "options")


class PublicFormSerializer(serializers.ModelSerializer):
    fields = PublicFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ("uuid", "title", "description", "visibility", "enforce_field_order", "fields")
