from datetime import datetime
from decimal import Decimal, InvalidOperation

from apps.core.exceptions import DomainError

from .base import BaseFieldHandler, FieldRegistry, ParsedAnswer


@FieldRegistry.register
class TextHandler(BaseFieldHandler):
    type = "text"
    config_schema = {"min_length": int, "max_length": int, "regex": str, "placeholder": str}
    aggregation = "list"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        text = str(raw or "")
        cfg = field.config or {}
        if "min_length" in cfg and len(text) < cfg["min_length"]:
            raise DomainError(f"«{field.label}» باید حداقل {cfg['min_length']} کاراکتر باشد.", code="text_min")
        if "max_length" in cfg and len(text) > cfg["max_length"]:
            raise DomainError(f"«{field.label}» باید حداکثر {cfg['max_length']} کاراکتر باشد.", code="text_max")
        if "regex" in cfg:
            import re

            if not re.match(cfg["regex"], text):
                raise DomainError(f"«{field.label}» با الگوی موردنیاز مطابقت ندارد.", code="text_regex")
        return ParsedAnswer(value=text, value_text=text)


@FieldRegistry.register
class TextareaHandler(TextHandler):
    type = "textarea"
    config_schema = {"min_length": int, "max_length": int, "rows": int}


@FieldRegistry.register
class NumberHandler(BaseFieldHandler):
    type = "number"
    config_schema = {"min": float, "max": float, "step": float, "is_integer": bool, "unit": str}
    aggregation = "numeric"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        try:
            num = Decimal(str(raw))
        except (InvalidOperation, TypeError):
            raise DomainError(f"«{field.label}» باید عدد باشد.", code="invalid_number")
        cfg = field.config or {}
        if cfg.get("is_integer") and num % 1 != 0:
            raise DomainError(f"«{field.label}» باید عدد صحیح باشد.", code="number_not_integer")
        if "min" in cfg and num < Decimal(str(cfg["min"])):
            raise DomainError(f"«{field.label}» نباید کمتر از {cfg['min']} باشد.", code="number_min")
        if "max" in cfg and num > Decimal(str(cfg["max"])):
            raise DomainError(f"«{field.label}» نباید بیشتر از {cfg['max']} باشد.", code="number_max")
        return ParsedAnswer(value=float(num), value_number=num)


@FieldRegistry.register
class SelectHandler(BaseFieldHandler):
    type = "select"
    config_schema = {"multiple": bool, "allow_other": bool}
    requires_options = True
    aggregation = "distribution"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        cfg = field.config or {}
        allow_other = cfg.get("allow_other", False)
        valid_values = set(field.options.values_list("value", flat=True))
        if raw not in valid_values and not allow_other:
            raise DomainError(f"گزینه‌ی نامعتبر برای «{field.label}».", code="invalid_option")
        return ParsedAnswer(value=raw, option_values=[raw] if raw in valid_values else [])


@FieldRegistry.register
class CheckboxHandler(BaseFieldHandler):
    type = "checkbox"
    config_schema = {"min_selected": int, "max_selected": int}
    requires_options = True
    aggregation = "distribution"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        values = raw or []
        if not isinstance(values, list):
            raise DomainError(f"«{field.label}» باید لیستی از گزینه‌ها باشد.", code="invalid_checkbox")
        cfg = field.config or {}
        if "min_selected" in cfg and len(values) < cfg["min_selected"]:
            raise DomainError(f"حداقل {cfg['min_selected']} گزینه برای «{field.label}» انتخاب کنید.", code="checkbox_min")
        if "max_selected" in cfg and len(values) > cfg["max_selected"]:
            raise DomainError(f"حداکثر {cfg['max_selected']} گزینه برای «{field.label}» مجاز است.", code="checkbox_max")
        valid_values = set(field.options.values_list("value", flat=True))
        invalid = set(values) - valid_values
        if invalid:
            raise DomainError(f"گزینه‌های نامعتبر: {sorted(invalid)}", code="invalid_option")
        return ParsedAnswer(value=values, option_values=values)


@FieldRegistry.register
class RatingHandler(BaseFieldHandler):
    type = "rating"
    config_schema = {"max_value": int, "allow_half": bool, "icon": str}
    aggregation = "numeric"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        cfg = field.config or {}
        max_value = cfg.get("max_value", 5)
        try:
            num = Decimal(str(raw))
        except (InvalidOperation, TypeError):
            raise DomainError(f"«{field.label}» نامعتبر است.", code="invalid_rating")
        if not (0 < num <= max_value):
            raise DomainError(f"امتیاز باید بین ۱ تا {max_value} باشد.", code="rating_range")
        if not cfg.get("allow_half", False) and num % 1 != 0:
            raise DomainError("امتیاز اعشاری مجاز نیست.", code="rating_half_not_allowed")
        return ParsedAnswer(value=float(num), value_number=num)


@FieldRegistry.register
class DateHandler(BaseFieldHandler):
    type = "date"
    config_schema = {"min_date": str, "max_date": str, "include_time": bool}
    aggregation = "timeline"

    def validate_answer(self, field, raw) -> ParsedAnswer:
        try:
            parsed = datetime.fromisoformat(str(raw))
        except ValueError:
            raise DomainError(f"«{field.label}» باید تاریخ ISO باشد.", code="invalid_date")
        cfg = field.config or {}
        if "min_date" in cfg and str(raw) < cfg["min_date"]:
            raise DomainError(f"«{field.label}» نباید زودتر از {cfg['min_date']} باشد.", code="date_min")
        if "max_date" in cfg and str(raw) > cfg["max_date"]:
            raise DomainError(f"«{field.label}» نباید دیرتر از {cfg['max_date']} باشد.", code="date_max")
        return ParsedAnswer(value=str(raw), value_date=parsed)
