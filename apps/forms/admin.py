from django.contrib import admin

from .models import Answer, AnswerOption, Field, FieldOption, Form, Submission


class FieldOptionInline(admin.TabularInline):
    model = FieldOption
    extra = 0


class FieldInline(admin.TabularInline):
    model = Field
    extra = 0
    show_change_link = True


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "is_active", "category", "created_at")
    list_filter = ("visibility", "is_active", "enforce_field_order", "category")
    search_fields = ("title", "uuid", "owner__username", "owner__email")
    readonly_fields = ("uuid", "created_at", "updated_at")
    inlines = (FieldInline,)


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("label", "form", "type", "order", "is_required")
    list_filter = ("type", "is_required")
    search_fields = ("label", "form__title")
    inlines = (FieldOptionInline,)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "form", "respondent", "is_complete", "created_at", "completed_at")
    list_filter = ("is_complete", "created_at")
    search_fields = ("id", "form__title", "respondent__username", "session_key")
    readonly_fields = tuple(field.name for field in Submission._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "field")
    readonly_fields = tuple(field.name for field in Answer._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("answer", "option")
    readonly_fields = tuple(field.name for field in AnswerOption._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
