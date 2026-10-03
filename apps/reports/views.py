from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.forms.models import Field, Form
from apps.processes.models import Process

from .models import ReportSchedule
from .serializers import ReportScheduleSerializer
from .services import aggregate_field, form_report, process_report, text_answer_page


class FormReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request, uuid):
        form = get_object_or_404(Form, uuid=uuid, owner=request.user)
        return Response(form_report(form))


class ProcessReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request, uuid):
        process = get_object_or_404(Process, uuid=uuid, owner=request.user)
        return Response(process_report(process))


class FieldReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("page", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("page_size", int, OpenApiParameter.QUERY, required=False),
        ],
        responses=dict,
    )
    def get(self, request, field_id):
        field = get_object_or_404(Field, id=field_id, form__owner=request.user)
        if field.type in {"text", "textarea"}:
            return Response(
                text_answer_page(
                    field,
                    request.query_params.get("page", 1),
                    request.query_params.get("page_size", 20),
                )
            )
        return Response(aggregate_field(field))


class StatsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request):
        from apps.forms.models import Submission

        form_qs = Form.objects.filter(owner=request.user)
        process_qs = Process.objects.filter(owner=request.user)
        submissions = Submission.objects.filter(form__owner=request.user, is_complete=True).count()
        return Response(
            {
                "forms": form_qs.count(),
                "processes": process_qs.count(),
                "completed_submissions": submissions,
                "active_forms": form_qs.filter(is_active=True).count(),
                "active_processes": process_qs.filter(is_active=True).count(),
            }
        )


@extend_schema_view(
    list=extend_schema(responses=ReportScheduleSerializer(many=True)),
    retrieve=extend_schema(responses=ReportScheduleSerializer),
    create=extend_schema(request=ReportScheduleSerializer, responses=ReportScheduleSerializer),
    update=extend_schema(request=ReportScheduleSerializer, responses=ReportScheduleSerializer),
    partial_update=extend_schema(request=ReportScheduleSerializer, responses=ReportScheduleSerializer),
    destroy=extend_schema(responses=None),
)
class ReportScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReportSchedule.objects.filter(owner=self.request.user).select_related("owner")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
