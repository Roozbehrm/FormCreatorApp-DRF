# اپ core — مالک: روزبه

این اپ پیش‌نیاز همه‌ی اپ‌های دیگر است — تا این‌جا تمام نشود بقیه نمی‌توانند migration بزنند.

- [ ] `models.py`: TimeStampedModel، UUIDModel، Visibility، ShareableModel — برنچ `feature/1-core-base-models`
- [ ] `exceptions.py`: DomainError/StepLocked/AccessDenied + api_exception_handler — برنچ `feature/25-core-utils`
- [ ] `pagination.py`: StandardPagination — برنچ `feature/25-core-utils`
- [ ] `permissions.py`: IsOwner — برنچ `feature/25-core-utils`
- [ ] `cache.py`: کلیدهای استاندارد کش — برنچ `feature/25-core-utils`
## تست
- [ ] `DomainError`: status_code و code درست برمی‌گردد؛ `StepLocked`→409، `AccessDenied`→403
- [ ] `api_exception_handler`: خروجی خطای اعتبارسنجی DRF هم به فرمت یکدست `{"error": {...}}` تبدیل می‌شود
- [ ] `StandardPagination`: page_size پیش‌فرض ۲۰؛ `?page_size=` کار می‌کند؛ بیشتر از `max_page_size` رد می‌شود
- [ ] `IsOwner`: مالک عبور می‌کند، غیرمالک ۴۰۳/۴۰۴ می‌گیرد
- [ ] `cache.py`: کلیدها به‌درستی ساخته می‌شوند؛ `invalidate_form` هر دو کلید را پاک می‌کند
