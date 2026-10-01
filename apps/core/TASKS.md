# اپ core — مالک: روزبه

این اپ پیش‌نیاز همه‌ی اپ‌های دیگر است — تا این‌جا تمام نشود بقیه نمی‌توانند migration بزنند.

- [ ] `models.py`: TimeStampedModel، UUIDModel، Visibility، ShareableModel — برنچ `feature/3-core-base-models`
- [ ] `exceptions.py`: DomainError/StepLocked/AccessDenied + api_exception_handler — برنچ `feature/4-core-utils`
- [ ] `pagination.py`: StandardPagination — برنچ `feature/4-core-utils`
- [ ] `permissions.py`: IsOwner — برنچ `feature/4-core-utils`
- [ ] `cache.py`: کلیدهای استاندارد کش — برنچ `feature/4-core-utils`

> **استثنا:** `access.py` (توکن دسترسی موقت برای فرم/فرایند خصوصی: `make_access_token`/`has_valid_access`/`assert_owns`) هم فیزیکاً داخل همین پوشه ساخته می‌شود، اما مالکیتش با **مهیار** است (بخشی از تسک #۱۸، نه از تسک‌های این فایل) — چون این توکن بین اپ‌های forms و processes مشترک است و منطقی‌تر است یک‌بار در core نوشته شود تا در هر اپ تکرار شود. روزبه این فایل را در برنچ `feature/4-core-utils` نمی‌سازد؛ فقط باید `exceptions.py` (که مهیار در #۱۸ به `AccessDenied` از آن نیاز دارد) قبل از شروع او مرج شده باشد.

## تست
- [ ] `DomainError`: status_code و code درست برمی‌گردد؛ `StepLocked`→409، `AccessDenied`→403
- [ ] `api_exception_handler`: خروجی خطای اعتبارسنجی DRF هم به فرمت یکدست `{"error": {...}}` تبدیل می‌شود
- [ ] `StandardPagination`: page_size پیش‌فرض ۲۰؛ `?page_size=` کار می‌کند؛ بیشتر از `max_page_size` رد می‌شود
- [ ] `IsOwner`: مالک عبور می‌کند، غیرمالک ۴۰۳/۴۰۴ می‌گیرد
- [ ] `cache.py`: کلیدها به‌درستی ساخته می‌شوند؛ `invalidate_form` هر دو کلید را پاک می‌کند
