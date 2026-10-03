from secrets import token_urlsafe

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.access import assert_private_access, make_access_token
from apps.core.cache import invalidate_process
from apps.core.exceptions import DomainError
from apps.core.permissions import IsOwner
from apps.forms.services import submit_form

from .models import Process, ProcessRun, ProcessStep
from .serializers import (
    ProcessSerializer,
    ProcessStepSerializer,
    PublicProcessRunSerializer,
    PublicProcessSerializer,
    PublicProcessStateSerializer,
)
from .services import assert_step_unlocked, complete_step, next_step_for_run


def _session_key_without_supplied_value(request):
    if request.session.session_key:
        return request.session.session_key
    request.session.create()
    return request.session.session_key or token_urlsafe(24)


def _session_key(request):
    key = request.headers.get("X-Session-Key") or request.data.get("session_key")
    if key is not None:
        if not isinstance(key, str):
            raise serializers.ValidationError({"session_key": "session_key باید رشته باشد."})
        key = key.strip()
        if not key:
            return _session_key_without_supplied_value(request)
        if len(key) > 64:
            raise serializers.ValidationError({"session_key": "session_key نباید بیشتر از ۶۴ کاراکتر باشد."})
        return key
    if request.session.session_key:
        return request.session.session_key
    request.session.create()
    return request.session.session_key or token_urlsafe(24)


def get_or_create_run(process, request, session_key):
    respondent = request.user if request.user.is_authenticated else None
    filters = {"process": process, "status": "in_progress"}
    if respondent:
        filters["respondent"] = respondent
    else:
        filters["session_key"] = session_key
    run = ProcessRun.objects.filter(**filters).order_by("-created_at").first()
    if run:
        return run
    return ProcessRun.objects.create(
        process=process,
        respondent=respondent,
        session_key=session_key,
    )


def _public_state(process, run, session_key):
    return {
        "process": PublicProcessSerializer(process).data,
        "run": PublicProcessRunSerializer(run).data,
        "completed_step_ids": list(run.completions.values_list("step_id", flat=True)),
        "next_step_id": getattr(next_step_for_run(run), "id", None),
        "session_key": session_key,
    }


@extend_schema_view(
    list=extend_schema(responses=ProcessSerializer(many=True)),
    retrieve=extend_schema(responses=ProcessSerializer),
    create=extend_schema(request=ProcessSerializer, responses=ProcessSerializer),
    update=extend_schema(request=ProcessSerializer, responses=ProcessSerializer),
    partial_update=extend_schema(request=ProcessSerializer, responses=ProcessSerializer),
    destroy=extend_schema(responses=None),
)
class ProcessViewSet(viewsets.ModelViewSet):
    serializer_class = ProcessSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        process = serializer.save()
        invalidate_process(process.id)

    def perform_update(self, serializer):
        process = serializer.save()
        invalidate_process(process.id)

    def perform_destroy(self, instance):
        process_id = instance.id
        instance.delete()
        invalidate_process(process_id)

    def get_queryset(self):
        qs = (
            Process.objects.filter(owner=self.request.user)
            .select_related("category")
            .prefetch_related("steps__form")
        )
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs


@extend_schema_view(
    list=extend_schema(responses=ProcessStepSerializer(many=True)),
    retrieve=extend_schema(responses=ProcessStepSerializer),
    create=extend_schema(request=ProcessStepSerializer, responses=ProcessStepSerializer),
    update=extend_schema(request=ProcessStepSerializer, responses=ProcessStepSerializer),
    partial_update=extend_schema(request=ProcessStepSerializer, responses=ProcessStepSerializer),
    destroy=extend_schema(responses=None),
)
class ProcessStepViewSet(viewsets.ModelViewSet):
    serializer_class = ProcessStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_process(self):
        return get_object_or_404(
            Process,
            uuid=self.kwargs["process_uuid"],
            owner=self.request.user,
        )

    def get_queryset(self):
        return ProcessStep.objects.filter(process=self.get_process()).select_related("form")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["process"] = self.get_process()
        return context

    def perform_create(self, serializer):
        process = self.get_process()
        serializer.save(process=process)
        invalidate_process(process.id)

    def perform_update(self, serializer):
        process = self.get_process()
        serializer.save()
        invalidate_process(process.id)

    def perform_destroy(self, instance):
        process = instance.process
        instance.delete()
        invalidate_process(process.id)


class PublicProcessView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=PublicProcessSerializer)
    def get(self, request, uuid):
        process = get_object_or_404(
            Process.objects.prefetch_related("steps__form__fields__options"),
            uuid=uuid,
            is_active=True,
        )
        assert_private_access(process, request, "process")
        from apps.reports.services import record_visit

        record_visit("process", process.id)
        return Response(PublicProcessSerializer(process).data)


class ProcessUnlockView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "unlock"

    @extend_schema(
        request=dict,
        responses={200: OpenApiResponse(description="Temporary process access token")},
    )
    def post(self, request, uuid):
        process = get_object_or_404(Process, uuid=uuid, is_active=True)
        password = request.data.get("password", "")
        if not process.is_private or not process.check_access_password(password):
            raise DomainError(
                "گذرواژه‌ی فرایند نادرست است.",
                code="invalid_password",
                status_code=403,
            )
        return Response({"access_token": make_access_token("process", process.id)})


class PublicProcessStateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=PublicProcessStateSerializer)
    def get(self, request, uuid):
        process = get_object_or_404(
            Process.objects.prefetch_related("steps__form"),
            uuid=uuid,
            is_active=True,
        )
        assert_private_access(process, request, "process")
        session_key = _session_key(request)
        run = get_or_create_run(process, request, session_key)
        return Response(_public_state(process, run, session_key))


class PublicProcessStepSubmitView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=dict,
        responses=PublicProcessStateSerializer,
    )
    def post(self, request, uuid, step_id):
        process = get_object_or_404(Process, uuid=uuid, is_active=True)
        assert_private_access(process, request, "process")
        step = get_object_or_404(ProcessStep, id=step_id, process=process)
        session_key = _session_key(request)
        run = get_or_create_run(process, request, session_key)
        assert_step_unlocked(run, step)

        answers = request.data.get("answers", {})
        if not isinstance(answers, dict):
            raise serializers.ValidationError({"answers": "answers باید یک شیء باشد."})
        submission = submit_form(
            form=step.form,
            data=answers,
            respondent=run.respondent,
            session_key=session_key,
            ip=request.META.get("REMOTE_ADDR"),
            process_run=run,
        )
        complete_step(run, step, submission)
        run.refresh_from_db()
        return Response(
            _public_state(process, run, session_key) | {"submission_id": submission.id},
            status=status.HTTP_201_CREATED,
        )
