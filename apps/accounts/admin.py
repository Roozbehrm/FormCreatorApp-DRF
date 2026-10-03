from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTPRequestLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("FormFlow", {"fields": ("phone", "is_verified")}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("FormFlow", {"fields": ("phone", "email", "is_verified")}),)
    list_display = ("username", "email", "phone", "is_verified", "is_staff")
    search_fields = ("username", "email", "phone")


@admin.register(OTPRequestLog)
class OTPRequestLogAdmin(admin.ModelAdmin):
    list_display = ("identifier", "purpose", "is_verified", "attempts", "ip", "created_at")
    list_filter = ("purpose", "is_verified")
    search_fields = ("identifier", "ip")
    readonly_fields = tuple(field.name for field in OTPRequestLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
