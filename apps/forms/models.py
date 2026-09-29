"""
مالک: روزبه (پیش از شروع کار فائزه روی سریالایزر/ویو)
TODO:
  - FieldType(TextChoices)      text | textarea | number | select | checkbox | rating | date
  - Form(ShareableModel)        owner، category (FK nullable)، accepts_responses_until،
        enforce_field_order (بولین، پیش‌فرض False) — اگر True باشد، سوالات فرم باید به ترتیب
        `order` جواب داده شوند (مثل حالت آزمون: سوال ۲ تا سوال ۱ جواب داده نشده باز نمی‌شود)
  - Field(TimeStampedModel)     form، type، label، help_text، order، is_required، config (JSONField)
  - FieldOption                 field، label، value، order   (برای select/checkbox)
  - Submission(TimeStampedModel)
        form، process_run (FK nullable)، respondent (FK nullable)، session_key، ip،
        is_complete (پیش‌فرض False — چون حالا ذخیره تدریجی است)، completed_at (nullable،
        وقتی finalize_submission صدا زده می‌شود پر می‌شود)
  - Answer
        submission، field، value (JSONField)، value_number، value_date، value_text
        (ذخیره ترکیبی: خام در value + denormalize در ستون‌های عددی/تاریخ برای گزارش سریع)
  - AnswerOption                answer، option   (برای تجمیع سریع گزینه‌ها)

پیش‌نیاز: apps/core/models.py (ShareableModel/TimeStampedModel) باید قبلش تمام شده باشد.
"""
