"""
مالک: روزبه (پیش از شروع کار فائزه)
TODO:
  - ParsedAnswer (dataclass)     value، value_number، value_date، value_text، option_values
  - BaseFieldHandler
        validate_config(config: dict) -> dict     اعتبارسنجی تنظیمات هنگام ساخت فرم
        validate_answer(field, raw) -> ParsedAnswer   اعتبارسنجی پاسخ هنگام ثبت
        aggregate_spec(field) -> dict              نوع تجمیع برای گزارش (numeric/distribution/timeline/list)
  - FieldRegistry
        register(handler_cls) / get(field_type) -> BaseFieldHandler / all() -> dict

این فایل قرارداد مشترک بین forms و reports است — بعد از تکمیم، امضای متدها را با علی هم در میان بگذار.
"""
