"""
مالک: روزبه (پیش از شروع کار علی)
TODO:
  - aggregate_field(field) -> dict
        بر اساس FieldRegistry.get(field.type).aggregate_spec(field):
        numeric -> count/avg/min/max/sum ، distribution -> توزیع درصدی گزینه‌ها ،
        timeline -> سری زمانی بر پایه value_date ، list -> نمونه پاسخ‌های متنی
  - form_report(form) -> dict         تجمیع همه فیلدهای یک فرم + تعداد پاسخ‌ها
  - process_report(process) -> dict   تجمیع یکپارچه همه فرم‌های یک فرایند

پیش‌نیاز: apps/forms/fields/base.py (FieldRegistry) و apps/forms/models.py باید تمام شده باشند.
"""
