import csv
from io import BytesIO
from secrets import token_urlsafe

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from openpyxl import Workbook
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.access import assert_owns, assert_private_access, make_access_token
from apps.core.cache import form_schema_key
from apps.core.exceptions import AccessDenied, DomainError
from apps.core.permissions import IsOwner
from apps.forms.models import Field, Form, Submission
from apps.forms.serializers import (
    FieldBulkReorderSerializer,
    FieldSerializer,
    FormDetailSerializer,
    FormSerializer,
    PublicFormSerializer,
)
from apps.forms.services import finalize_submission, start_submission, submit_field_answer, submit_form
from apps.reports.services import record_visit


def _public_form(uuid, request):
    form = get_object_or_404(
        Form.objects.prefetch_related("fields__options"),
        uuid=uuid,
        is_active=True,
    )
    assert_private_access(form, request, "form")
    return form


def _public_session_key(request) -> str:
    if "session_key" in request.data:
        raise AccessDenied("کلید نشست را نمی‌توان از طریق بدنه‌ی درخواست تعیین کرد.", code="session_key_forbidden")
    session_key = request.headers.get("X-Session-Key")
    if session_key is None or session_key == "":
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key or token_urlsafe(32)
    if not isinstance(session_key, str):
        raise serializers.ValidationError({"session_key": "session_key باید رشته باشد."})
    session_key = session_key.strip()
    if not session_key or len(session_key) > 64:
        raise serializers.ValidationError({"session_key": "session_key نامعتبر است."})
    return session_key

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
        queryset = Form.objects.filter(owner=self.request.user)
        category_id = self.request.query_params.get("category")
        if category_id:
            if not category_id.isdecimal():
                return queryset.none()
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FormDetailSerializer

        return FormSerializer

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(responses=dict)
    @action(detail=True, methods=["get"], url_path="submissions")
    def submissions(self, request, uuid=None):
        form = self.get_object()
        fields = list(form.fields.all())
        submissions = (
            form.submissions.filter(is_complete=True)
            .select_related("respondent")
            .prefetch_related("answers__selected_options__option")
            .order_by("created_at", "id")
        )
        results = []
        for submission in submissions:
            answers = {answer.field_id: answer for answer in submission.answers.all()}
            results.append(
                {
                    "id": submission.id,
                    "submitted_at": submission.completed_at,
                    "respondent_id": submission.respondent_id,
                    "answers": [
                        {
                            "field_id": field.id,
                            "label": field.label,
                            "value": _answer_display_value(answers.get(field.id)),
                        }
                        for field in fields
                    ],
                }
            )
        return Response({"count": len(results), "results": results})

    @extend_schema(
        parameters=[OpenApiParameter("format", str, OpenApiParameter.QUERY, enum=["csv", "xlsx"])],
        responses={200: OpenApiResponse(description="CSV or Excel export of completed submissions")},
    )
    @action(detail=True, methods=["get"], url_path="export")
    def export(self, request, uuid=None):
        form = self.get_object()
        export_format = request.query_params.get("format", "csv").lower()
        if export_format not in {"csv", "xlsx"}:
            raise serializers.ValidationError({"format": "format must be csv or xlsx."})

        fields = list(form.fields.all())
        submissions = (
            form.submissions.filter(is_complete=True)
            .prefetch_related("answers__selected_options__option")
            .order_by("created_at", "id")
        )
        headers = ["submission_id", "submitted_at", *(field.label for field in fields)]
        rows = [headers]
        for submission in submissions:
            answers = {answer.field_id: answer for answer in submission.answers.all()}
            rows.append(
                [
                    submission.id,
                    submission.completed_at.isoformat() if submission.completed_at else "",
                    *(_answer_display_value(answers.get(field.id)) or "" for field in fields),
                ]
            )

        filename = f"form-{form.uuid}-submissions"
        if export_format == "csv":
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
            response.write("\ufeff")
            writer = csv.writer(response)
            writer.writerows(rows)
            return response

        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet("Submissions")
        for row in rows:
            worksheet.append(row)
        output = BytesIO()
        workbook.save(output)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
        return response


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

    def perform_destroy(self, instance):
        if instance.form.submissions.filter(is_complete=True).exists():
            raise DomainError(
                "پس از ثبت پاسخ، حذف فیلد مجاز نیست.",
                code="field_schema_locked",
                status_code=409,
            )
        super().perform_destroy(instance)

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


class PublicFormView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=PublicFormSerializer)
    def get(self, request, uuid):
        form = _public_form(uuid, request)
        cache_key = form_schema_key(form.uuid)
        data = cache.get(cache_key)
        if data is None:
            data = PublicFormSerializer(form).data
            cache.set(cache_key, data, settings.CACHE_TTL_FORM_SCHEMA)
        record_visit("form", form.id)
        return Response(data)


class FormUnlockView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "unlock"

    @extend_schema(request=dict, responses={200: OpenApiResponse(description="Temporary form access token")})
    def post(self, request, uuid):
        form = get_object_or_404(Form, uuid=uuid, is_active=True)
        password = request.data.get("password", "")
        if not form.is_private or not form.check_access_password(password):
            raise DomainError("گذرواژه‌ی فرم نادرست است.", code="invalid_password", status_code=403)
        return Response({"access_token": make_access_token("form", form.id)})


class PublicFormSubmitView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=dict, responses={201: dict})
    def post(self, request, uuid):
        form = _public_form(uuid, request)
        answers = request.data.get("answers", {})
        if not isinstance(answers, dict):
            raise serializers.ValidationError({"answers": "answers باید یک شیء باشد."})
        session_key = _public_session_key(request)
        submission = submit_form(
            form=form,
            data=answers,
            respondent=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip=request.META.get("REMOTE_ADDR"),
        )
        return Response(
            {"submission_id": submission.id, "session_key": session_key, "is_complete": submission.is_complete},
            status=201,
        )


class PublicSubmissionStartView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=dict, responses={201: dict})
    def post(self, request, uuid):
        form = _public_form(uuid, request)
        session_key = _public_session_key(request)
        submission = start_submission(
            form=form,
            respondent=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip=request.META.get("REMOTE_ADDR"),
        )
        return Response({"submission_id": submission.id, "session_key": session_key}, status=201)


class PublicSubmissionAnswerView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=dict, responses={200: dict})
    def post(self, request, uuid, submission_id, field_id):
        form = _public_form(uuid, request)
        submission = get_object_or_404(Submission, id=submission_id, form=form)
        assert_owns(submission, request)
        field = get_object_or_404(Field, id=field_id, form=form)
        answer = submit_field_answer(submission=submission, field=field, raw=request.data.get("answer"))
        return Response({"field_id": field.id, "answer_id": answer.id if answer else None, "saved": True})


class PublicSubmissionFinalizeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: dict})
    def post(self, request, uuid, submission_id):
        form = _public_form(uuid, request)
        submission = get_object_or_404(Submission, id=submission_id, form=form)
        assert_owns(submission, request)
        finalize_submission(submission)
        return Response({"submission_id": submission.id, "is_complete": submission.is_complete})


def _answer_display_value(answer):
    if answer is None:
        return None
    selected_labels = [link.option.label for link in answer.selected_options.all()]
    if selected_labels:
        return ", ".join(selected_labels)
    if answer.value_text:
        return answer.value_text
    if answer.value_number is not None:
        return str(answer.value_number)
    if answer.value_date is not None:
        return answer.value_date.isoformat()
    return answer.value
