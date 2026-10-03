# پایه معماری — مسئول: روزبه (به‌جز #1)

فایل‌های زیر عمداً خالی و TODO نگه داشته شده‌اند تا **قبل از شروع کار بقیه** نوشته شوند.
دلیلش این است که مدل‌های دیتابیس و قرارداد بین ماژول‌ها (مثل موتور فیلد پویا) باید یک‌بار و
یکدست تعیین شوند، وگرنه هرکس نسخه‌ی خودش را می‌سازد و سر ادغام PR درگیر می‌شویم.
شماره‌ها = شماره‌ی ایشو = شماره‌ی برنچ (جدول کامل در `Documents/TASKS.md`).

## ⚠️ اول از همه: #1 (مدل User) و #4 (core utils)
پروژه تا این دو مرج نشوند اصلاً بالا نمی‌آید (`manage.py check` / `migrate` / `pytest` / CI خطا می‌دهند):
- `settings.AUTH_USER_MODEL = "accounts.User"` است ولی مدل هنوز وجود ندارد ← تسک #1 (مهیار)
- `REST_FRAMEWORK` به `apps.core.pagination.StandardPagination` و `apps.core.exceptions.api_exception_handler`
  اشاره می‌کند که هنوز نوشته نشده‌اند ← تسک #4 (روزبه)

پس این دو اولین PRها هستند. حتی CI خودِ PR شماره‌ی ۱ تا #4 مرج نشود کامل سبز نمی‌شود؛ برای همین این دو را
پشت‌سرهم و سریع مرج کن (یا اگر branch protection با «required checks» فعال است، تا این دو مرج نشده آن را روشن نکن).

## core
- [ ] `apps/core/models.py` — `feature/3-core-base-models`
- [ ] `apps/core/exceptions.py`, `pagination.py`, `permissions.py`, `cache.py` — `feature/4-core-utils`
  (تنظیمات DRF به `pagination` و `exceptions` اشاره می‌کنند؛ تا این برنچ مرج نشود هیچ view ای کار نمی‌کند)

## forms
- [ ] `apps/forms/models.py` — `feature/7-forms-models`
- [ ] `apps/forms/fields/base.py`, `handlers.py` — `feature/8-forms-field-engine`
- [ ] `apps/forms/services.py` — بخشی از `feature/8-forms-field-engine`

## processes
- [ ] `apps/processes/models.py` — `feature/9-processes-models`
- [ ] `apps/processes/services.py` — `feature/19-processes-linear-engine` (p1)

## reports
- [ ] `apps/reports/models.py`, `services.py` — `feature/10-reports-aggregation`
- [ ] `apps/reports/consumers.py`, `routing.py` — `feature/27-reports-realtime-ws` (امتیازی)

## ترتیب پیشنهادی مرج
1. `#1` (User) + `#4` (core utils) ← بلاک‌کننده‌ها، `#3` (core models) موازی با آن‌ها
2. `#7` forms-models ← `#8` forms-field-engine
3. `#9` processes-models
4. `#10` reports-aggregation
5. `#5` و `#6` (تست/CI) موازی با بالا
6. بقیه‌ی تسک‌ها (`p1`) بعد از مرج وابستگی‌هایشان؛ ستون «وابسته به» در `TASKS.md` را ببین.

بعد از هر مرج پایه به `dev`، به بقیه خبر بده تا `git fetch && git rebase origin/dev` بزنند.
