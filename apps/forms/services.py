"""
مالک: روزبه (پیش از شروع کار فائزه)

تصمیم: ذخیره‌ی تدریجی (هر جواب همان لحظه ثبت می‌شود) رفتار پیش‌فرض همه‌ی فرم‌هاست —
نه فقط فرم‌های ترتیبی — تا با قطعی شبکه، فقط آخرین جواب از دست برود نه کل فرم.
«ذخیره‌ی تدریجی» و «قفل ترتیب سوالات» دو چیز جدا هستند؛ enforce_field_order فقط دومی را کنترل می‌کند.

TODO:
  start_submission(*, form, respondent=None, session_key="", ip=None, process_run=None) -> Submission
    - نقطه‌ی شروع استاندارد برای پاسخ به هر فرمی (نه فقط ترتیبی)
    - یک Submission با is_complete=False می‌سازد

  assert_field_unlocked(submission, field) -> None
    - فقط وقتی form.enforce_field_order=True معنی دارد: اگر سوالی با order کمتر از field.order
      هنوز در این submission جواب داده نشده، apps.core.exceptions.StepLocked بینداز (۴۰۹)
    - اگر enforce_field_order=False، همیشه عبور کن (فقط چک کن field واقعاً متعلق به همین form است)

  submit_field_answer(submission, field, raw) -> Answer
    - مسیر استاندارد ثبت پاسخ برای همه‌ی فرم‌ها؛ هر بار صدا زده می‌شود یک سوال جواب داده شد
    - assert_field_unlocked را صدا بزن (خودش تصمیم می‌گیرد قفل کند یا نه)
    - با FieldRegistry اعتبارسنجی کن، Answer بساز/آپدیت کن (اگر جواب قبلی داشت، override کن)
    - اگر همه‌ی فیلدهای اجباری فرم جواب دارند، submission.is_complete = True کن

  finalize_submission(submission) -> Submission
    - چک نهایی: همه‌ی فیلدهای is_required=True جواب دارند؟ اگر نه DomainError بده
    - is_complete=True و زمان تکمیل را ثبت کن (برای گزارش «چند نفر فرم را رها کردند» به علی کمک می‌کند)

  submit_form(*, form, data: dict, ...) -> Submission   [فقط برای واردات دسته‌ای/اسکریپت]
    - نسخه‌ی یک‌جا: همه‌ی فیلدها را با هم می‌گیرد و اتمیک ثبت می‌کند
    - برای وارد کردن دستی داده (مثلاً import از یک فایل CSV قدیمی) استفاده می‌شود، نه مسیر پاسخ‌دهی عمومی
"""
