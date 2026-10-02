from django.contrib import admin

from .models import Answer, AnswerOption, Field, FieldOption, Form, Submission


class FieldInline(admin.TabularInline):
    model = Field
    extra = 0


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "is_active", "created_at")
    list_filter = ("visibility", "is_active", "enforce_field_order")
    search_fields = ("title", "uuid")
    inlines = [FieldInline]


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("label", "form", "type", "order", "is_required")
    list_filter = ("type",)


admin.site.register(FieldOption)
admin.site.register(Submission)
admin.site.register(Answer)
admin.site.register(AnswerOption)
