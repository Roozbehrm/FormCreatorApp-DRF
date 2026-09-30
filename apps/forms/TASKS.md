# اپ forms — قلب پروژه

## بخش پایه (مالک: روزبه — باید قبل از بخش CRUD تمام شود)
- [ ] `models.py`: Form/Field/FieldOption/Submission/Answer/AnswerOption — برنچ `feature/7-forms-models`
- [ ] `fields/base.py` + `fields/handlers.py`: موتور فیلد پویا با هفت هندلر — برنچ `feature/8-forms-field-engine`
- [ ] `services.py`: submit_form (نسخه‌ی یک‌جا، فقط برای import دستی) — برنچ `feature/8-forms-field-engine`
- [ ] `services.py`: مسیر استاندارد ذخیره‌ی تدریجی برای **همه‌ی فرم‌ها** — start_submission،
      assert_field_unlocked (قفل ترتیب فقط اگر enforce_field_order=True)، submit_field_answer،
      finalize_submission — برنچ `feature/8-forms-field-engine`

## بخش CRUD/API (مالک: فائزه — بعد از تمام‌شدن بخش پایه)
- [ ] تعداد نامحدود فرم برای هر کاربر + تعداد دلخواه فیلد — `feature/15-forms-crud-api`
- [ ] لینک یکتا (uuid) برای اشتراک‌گذاری
- [ ] فرم عمومی/خصوصی + اتصال به مکانیزم گذرواژه مهیار
- [ ] endpoint اسکیمای عمومی فرم (کش‌شده) برای پاسخ‌دهنده — `feature/16-forms-public-submit`
- [ ] bulk reorder فیلدها
- [ ] مشاهده پاسخ‌های ارسالی + خروجی CSV/Excel — `feature/25-forms-export-csv`
- [ ] تکمیل قوانین دقیق اعتبارسنجی هر نوع فیلد (اگر روزبه فقط اسکلت گذاشته) — `feature/17-forms-field-validation`
- [ ] annotate همه endpointها با @extend_schema

## تست (هر هفت نوع، happy path + edge case) — مالک: فائزه — برنچ `test/31-forms-field-tests`
- [ ] config نامعتبر رد شود
- [ ] فیلد اجباری خالی = خطا
- [ ] عدد خارج از بازه، امتیاز بیشتر از max، تاریخ بدفرمت، گزینه ناموجود
- [ ] rollback کامل در صورت خطای یکی از فیلدها
- [ ] CRUD فرم: کاربر فقط فرم‌های خودش را در لیست می‌بیند، فرم کاربر دیگر ۴۰۴ می‌دهد
- [ ] endpoint عمومی فرم (`/public/forms/{uuid}/`) اطلاعات مالک (email و...) را لو نمی‌دهد
- [ ] فرم خصوصی بدون توکن دسترسی (unlock نشده) قابل مشاهده/پاسخ نیست
- [ ] خروجی CSV/Excel دقیقاً با تعداد و ترتیب پاسخ‌های واقعی مطابقت دارد
- [ ] فرم ترتیبی (`enforce_field_order=True`): جواب‌دادن به سوال ۲ قبل از سوال ۱ → ۴۰۹ (StepLocked)
- [ ] فرم غیرترتیبی (`enforce_field_order=False`): جواب‌دادن به سوال‌ها به هر ترتیبی، هرکدام تدریجی ذخیره می‌شود
- [ ] هر دو حالت: هر `submit_field_answer` بلافاصله در دیتابیس ذخیره می‌شود (نه در پایان)
- [ ] `finalize_submission`: اگر فیلد اجباری خالی مانده رد می‌شود؛ در غیر این صورت `is_complete=True` می‌کند
- [ ] قطع‌شدن وسط راه: جواب‌های ثبت‌شده‌ی قبلی در دیتابیس باقی می‌مانند (شبیه‌سازی با قطع درخواست بعدی)

## وابستگی
خروجی این اپ ورودی processes (روزبه) و reports (روزبه/علی) است.
ترتیب کامل در `Documents/FOUNDATION_PLAN.md`.
