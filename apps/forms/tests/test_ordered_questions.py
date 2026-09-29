"""
مالک: فائزه
TODO (چک‌لیست کامل در apps/forms/TASKS.md):
  - ذخیره‌ی تدریجی برای همه‌ی فرم‌ها: هر submit_field_answer بلافاصله در DB می‌نشیند
  - فرم با enforce_field_order=True: جواب‌دادن به سوال ۲ قبل از سوال ۱ → StepLocked (409)
  - فرم با enforce_field_order=False: جواب به هر ترتیبی پذیرفته می‌شود، هرکدام تدریجی ذخیره می‌شود
  - finalize_submission: فیلد اجباری خالی رد می‌شود؛ همه پر بود → is_complete=True
  - شبیه‌سازی قطعی شبکه: بعد از چند submit_field_answer موفق، جواب‌های قبلی در DB باقی می‌مانند
"""
