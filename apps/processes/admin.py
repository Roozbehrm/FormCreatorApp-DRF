from django.contrib import admin

from .models import Process, ProcessRun, ProcessStep, StepCompletion


class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 0


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "type", "is_active", "category", "created_at")
    list_filter = ("visibility", "type", "is_active", "category")
    search_fields = ("title", "uuid", "owner__username", "owner__email")
    readonly_fields = ("uuid", "created_at", "updated_at")
    inlines = (ProcessStepInline,)


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProcessRun)
class ProcessRunAdmin(ReadOnlyAdmin):
    list_display = ("id", "process", "respondent", "session_key", "status", "completed_at", "created_at")
    readonly_fields = tuple(field.name for field in ProcessRun._meta.fields)
    search_fields = ("session_key", "process__title", "respondent__username")


@admin.register(StepCompletion)
class StepCompletionAdmin(ReadOnlyAdmin):
    list_display = ("id", "run", "step", "submission", "completed_at")
    readonly_fields = tuple(field.name for field in StepCompletion._meta.fields)
