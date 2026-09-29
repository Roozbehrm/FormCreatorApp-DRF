"""
مالک: فائزه
TODO:
  FormViewSet            CRUD  /forms/
  FieldViewSet           CRUD  /forms/{id}/fields/  + action bulk_reorder
  SubmissionListView     GET   /forms/{id}/submissions/
  FormExportView         GET   /forms/{id}/export/?format=csv
  PublicFormView         GET   /public/forms/{uuid}/        (کش، شمارش بازدید → علی)
  FormUnlockView         POST  /public/forms/{uuid}/unlock/ (مهیار)
  PublicSubmitView       POST  /public/forms/{uuid}/submit/ throttle_scope="submit"
        (ارسال یک‌جای همه‌ی جواب‌ها؛ فقط برای واردات دسته‌ای/دستی داده، نه مسیر پاسخ‌دهی عمومی)

  --- مسیر استاندارد (تدریجی، برای همه‌ی فرم‌ها) ---
  PublicStartSubmissionView   POST /public/forms/{uuid}/start/
        submission ناقص می‌سازد (start_submission)، id همان submission را برمی‌گرداند
  PublicAnswerFieldView       POST /public/forms/{uuid}/submissions/{submission_id}/answer/{field_id}/
        submit_field_answer را صدا می‌زند؛ برای فرم‌های enforce_field_order=True اگر سوال قبلی
        جواب داده نشده باشد ۴۰۹ برمی‌گرداند، برای بقیه‌ی فرم‌ها همیشه فقط ذخیره می‌کند
  PublicFinalizeSubmissionView POST /public/forms/{uuid}/submissions/{submission_id}/finalize/
        finalize_submission را صدا می‌زند؛ اگر فیلد اجباری خالی مانده خطا می‌دهد
"""
