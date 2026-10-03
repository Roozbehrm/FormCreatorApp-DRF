from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FieldReportView, FormReportView, ProcessReportView, ReportScheduleViewSet, StatsOverviewView

app_name = "reports"
router = DefaultRouter()
router.register("report-schedules", ReportScheduleViewSet, basename="report-schedule")

urlpatterns = router.urls + [
    path("forms/<uuid:uuid>/report/", FormReportView.as_view(), name="form-report"),
    path("processes/<uuid:uuid>/report/", ProcessReportView.as_view(), name="process-report"),
    path("fields/<int:field_id>/report/", FieldReportView.as_view(), name="field-report"),
    path("stats/overview/", StatsOverviewView.as_view(), name="stats-overview"),
]

