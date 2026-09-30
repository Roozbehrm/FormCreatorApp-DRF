# اپ reports

## بخش پایه (مالک: روزبه — باید قبل از بخش زیر تمام شود)
- [ ] `models.py`: VisitCounter/ReportSchedule/ReportDelivery — برنچ `feature/10-reports-aggregation`
- [ ] `services.py`: aggregate_field/form_report/process_report — برنچ `feature/10-reports-aggregation`
- [ ] `consumers.py` + `routing.py` (امتیازی، WebSocket) — برنچ `feature/27-reports-realtime-ws`
- [ ] GraphQL read-only (امتیازی) — برنچ `feature/28-graphql-reports`

## بخش سرویس/API (مالک: علی — بعد از تمام‌شدن بخش پایه)
- [ ] endpoint مشاهده گزارش فرم/فرایند روی سرویس‌های آماده — `feature/21-reports-view-api`
- [ ] شمارش بازدید با Redis + تسک flush + تعداد پاسخ‌ها — `feature/22-reports-visits`
- [ ] لایه کش نتایج تجمیع + ابطال با سیگنال ثبت پاسخ (هماهنگ با core/cache.py روزبه) — `feature/23-reports-cache`
- [ ] گزارش دوره‌ای: Celery Beat + قالب ایمیل + POST به webhook با HMAC و retry — `feature/24-reports-schedule-celery`
- [ ] لاگ ارسال‌ها (ReportDelivery) — `feature/24-reports-schedule-celery`

## تست — مالک: علی — برنچ `test/32-reports-tests`
- [ ] تجمیع عددی: میانگین/حداقل/حداکثر/مجموع درست با مقادیر مرزی (صفر، فقط یک پاسخ، بدون پاسخ)
- [ ] توزیع گزینه‌ها: جمع درصدها تقریباً ۱۰۰ می‌شود؛ گزینه‌ی بدون هیچ انتخابی هم در خروجی با count=0 دیده می‌شود
- [ ] سری زمانی (Date): گروه‌بندی بر اساس روز درست است
- [ ] لیست متنی (Text/Textarea): صفحه‌بندی درست کار می‌کند
- [ ] شمارنده‌ی بازدید: افزایش در Redis + تسک flush آن را درست به `VisitCounter` منتقل می‌کند (بدون از دست‌رفتن یا دوبار شمردن)
- [ ] ابطال کش: بعد از ثبت پاسخ جدید، درخواست بعدی گزارش، نسخه‌ی تازه می‌گیرد نه کش قدیمی
- [ ] تسک دوره‌ای: فقط `ReportSchedule`های سررسیدشده (بر اساس `last_run_at` و `period`) اجرا می‌شوند، نه همه
- [ ] webhook: امضای HMAC روی بدنه‌ی درخواست درست ساخته می‌شود؛ خطای شبکه باعث retry می‌شود (حداکثر ۳ بار)
- [ ] `ReportDelivery` هم برای موفق هم برای ناموفق لاگ می‌شود

## نکته
سیگنال لازم برای پوش گزارش برخط را در `apps/forms/signals.py` (با هماهنگی فائزه) صدا بزن؛
پیاده‌سازی خود کانال با روزبه است.
