"""
مالک: فائزه
TODO:
  FormViewSet            CRUD  /forms/
  FieldViewSet           CRUD  /forms/{id}/fields/  + action bulk_reorder
  SubmissionListView     GET   /forms/{id}/submissions/
  FormExportView         GET   /forms/{id}/export/?format=csv
  PublicFormView         GET   /public/forms/{uuid}/        (کش، شمارش بازدید → علی)
  FormUnlockView         POST  /public/forms/{uuid}/unlock/ (مهیار)
  PublicSubmitView       POST  /public/forms/{uuid}/submit/ throttle_scope="submit"
        (ارسال یک‌جای همه‌ی جواب‌ها؛ فقط برای واردات دسته‌ای/دستی داده، نه مسیر پاسخ‌دهی عمومی)

  --- مسیر استاندارد (تدریجی، برای همه‌ی فرم‌ها) ---
  PublicStartSubmissionView   POST /public/forms/{uuid}/start/
        submission ناقص می‌سازد (start_submission)، id همان submission را برمی‌گرداند
  PublicAnswerFieldView       POST /public/forms/{uuid}/submissions/{submission_id}/answer/{field_id}/
        submit_field_answer را صدا می‌زند؛ برای فرم‌های enforce_field_order=True اگر سوال قبلی
        جواب داده نشده باشد ۴۰۹ برمی‌گرداند، برای بقیه‌ی فرم‌ها همیشه فقط ذخیره می‌کند
  PublicFinalizeSubmissionView POST /public/forms/{uuid}/submissions/{submission_id}/finalize/
        finalize_submission را صدا می‌زند؛ اگر فیلد اجباری خالی مانده خطا می‌دهد
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsOwner
from apps.forms.models import Field, Form
from apps.forms.serializers import FieldBulkReorderSerializer, FieldSerializer, FormDetailSerializer, FormSerializer


@extend_schema_view(
    list=extend_schema(
        responses=FormSerializer(many=True),
        description="دریافت لیست فرم‌های متعلق به کاربر فعلی.",
    ),
    retrieve=extend_schema(
        responses=FormDetailSerializer,
        description="دریافت جزئیات یک فرم به همراه فیلدهای آن.",
    ),
    create=extend_schema(
        request=FormSerializer,
        responses=FormSerializer,
        description="ایجاد یک فرم جدید.",
    ),
    update=extend_schema(
        request=FormSerializer,
        responses=FormSerializer,
        description="ویرایش کامل یک فرم.",
    ),
    partial_update=extend_schema(
        request=FormSerializer,
        responses=FormSerializer,
        description="ویرایش بخشی از یک فرم.",
    ),
    destroy=extend_schema(
        responses=None,
        description="حذف یک فرم.",
    ),
)
class FormViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]

    lookup_field = "uuid"

    def get_queryset(self):
        return Form.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FormDetailSerializer

        return FormSerializer

    def perform_create(self, serializer):
        serializer.save()


@extend_schema_view(
    list=extend_schema(
        responses=FieldSerializer(many=True),
        description="دریافت فیلدهای یک فرم.",
    ),
    retrieve=extend_schema(
        responses=FieldSerializer,
        description="دریافت جزئیات یک فیلد.",
    ),
    create=extend_schema(
        request=FieldSerializer,
        responses=FieldSerializer,
        description="ایجاد فیلد برای یک فرم.",
    ),
    update=extend_schema(
        request=FieldSerializer,
        responses=FieldSerializer,
        description="ویرایش کامل یک فیلد.",
    ),
    partial_update=extend_schema(
        request=FieldSerializer,
        responses=FieldSerializer,
        description="ویرایش بخشی از یک فیلد.",
    ),
    destroy=extend_schema(
        responses=None,
        description="حذف یک فیلد.",
    ),
)
class FieldViewSet(viewsets.ModelViewSet):
    serializer_class = FieldSerializer
    permission_classes = [IsAuthenticated]

    def get_form(self):
        """
        فرم متعلق به کاربر فعلی را پیدا می‌کند.
        """
        return get_object_or_404(
            Form.objects.filter(owner=self.request.user),
            uuid=self.kwargs["form_uuid"],
        )

    def get_queryset(self):
        """
        فقط فیلدهای فرم مشخص‌ شده و متعلق به کاربر را برمی‌گرداند.
        """
        return Field.objects.filter(form=self.get_form())

    def perform_create(self, serializer):
        """
        فرم را از URL تعیین می‌کنیم، نه از داده ارسالی کاربر.
        """
        serializer.save(form=self.get_form())

    @extend_schema(
        request=FieldBulkReorderSerializer,
        responses={200: FieldSerializer(many=True)},
    )
    @action(detail=False, methods=["patch"], url_path="bulk-reorder")
    def bulk_reorder(self, request, form_uuid=None):
        serializer = FieldBulkReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data["fields"]
        field_ids = [item["id"] for item in items]

        with transaction.atomic():
            fields = list(self.get_queryset().filter(id__in=field_ids).order_by("id"))

            if len(fields) != len(field_ids):
                raise serializers.ValidationError("یک یا چند فیلد وجود ندارند یا متعلق به این فرم نیستند.")

            fields_by_id = {field.id: field for field in fields}

            for item in items:
                fields_by_id[item["id"]].order = item["order"]

            Field.objects.bulk_update(fields, ["order"])

        return Response(
            FieldSerializer(
                self.get_queryset(),
                many=True,
            ).data,
            status=200,
        )
