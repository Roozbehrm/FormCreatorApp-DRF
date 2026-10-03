from django.contrib import admin

from .models import ReportDelivery, ReportSchedule, VisitCounter


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "target_type", "object_id", "period", "delivery", "is_active", "last_run_at")
    list_filter = ("target_type", "period", "delivery", "is_active")
    search_fields = ("owner__username", "owner__email", "email", "webhook_url")
    readonly_fields = ("last_run_at", "created_at", "updated_at")


@admin.register(ReportDelivery)
class ReportDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "schedule", "is_success", "status_code", "created_at")
    list_filter = ("is_success", "status_code")
    readonly_fields = tuple(field.name for field in ReportDelivery._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VisitCounter)
class VisitCounterAdmin(admin.ModelAdmin):
    list_display = ("target_type", "object_id", "date", "count")
    list_filter = ("target_type", "date")
    readonly_fields = tuple(field.name for field in VisitCounter._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
