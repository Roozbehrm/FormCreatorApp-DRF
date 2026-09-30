"""
مالک: مهیار — تسک #36 (feature/36-accounts-admin)، بعد از مرج مدل‌ها در تسک #1 (روزبه)
TODO (تا مدل‌ها مرج نشده چیزی import نکن وگرنه پروژه بالا نمی‌آید):
  - @admin.register(User) class UserAdmin(django.contrib.auth.admin.UserAdmin)
        fieldsets/add_fieldsets را با phone و is_verified گسترش بده
        list_display: username, email, phone, is_verified, is_staff
        search_fields: username, email, phone
  - @admin.register(OTPRequestLog): فقط‌خواندنی (has_add_permission/has_change_permission = False)
        list_filter: purpose, is_verified
"""
