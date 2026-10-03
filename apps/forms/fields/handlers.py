import math
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.utils import timezone

from apps.core.exceptions import DomainError

from .base import BaseFieldHandler, FieldRegistry, ParsedAnswer


def _as_text(field, raw):
    if not isinstance(raw, str):
        raise DomainError(f"«{field.label}» باید متن باشد.", code="invalid_text")
    return raw


def _as_string_list(field, raw, error_code="invalid_option"):
    if not isinstance(raw, list) or not all(isinstance(value, str) for value in raw):
        raise DomainError(f"«{field.label}» باید لیستی از رشته‌ها باشد.", code=error_code)
    return raw


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if settings.USE_TZ and timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    if not settings.USE_TZ and timezone.is_aware(parsed):
        return timezone.make_naive(parsed, timezone.get_current_timezone())
    return parsed


@FieldRegistry.register
class TextHandler(BaseFieldHandler):
    type = "text"
    config_schema = {"min_length": int, "max_length": int, "regex": str, "placeholder": str}

    def validate_config(self, config):
        cfg = super().validate_config(config)
        if cfg.get("min_length", 0) < 0 or cfg.get("max_length", 0) < 0:
            raise DomainError("طول متن نمی‌تواند منفی باشد.", code="invalid_config")
        if "min_length" in cfg and "max_length" in cfg and cfg["min_length"] > cfg["max_length"]:
            raise DomainError("min_length نباید از max_length بیشتر باشد.", code="invalid_config")
        if "regex" in cfg:
            try:
                re.compile(cfg["regex"])
            except re.error as exc:
                raise DomainError("regex نامعتبر است.", code="invalid_config") from exc
        return cfg

    def validate_answer(self, field, raw):
        text = _as_text(field, raw)
        cfg = field.config or {}
        if "min_length" in cfg and len(text) < cfg["min_length"]:
            raise DomainError(
                f"«{field.label}» باید حداقل {cfg['min_length']} کاراکتر باشد.",
                code="text_min",
            )
        if "max_length" in cfg and len(text) > cfg["max_length"]:
            raise DomainError(
                f"«{field.label}» باید حداکثر {cfg['max_length']} کاراکتر باشد.",
                code="text_max",
            )
        if "regex" in cfg and re.fullmatch(cfg["regex"], text) is None:
            raise DomainError(
                f"«{field.label}» با الگوی موردنیاز مطابقت ندارد.",
                code="text_regex",
            )
        return ParsedAnswer(value=text, value_text=text)


@FieldRegistry.register
class TextareaHandler(TextHandler):
    type = "textarea"
    config_schema = {"min_length": int, "max_length": int, "rows": int}

    def validate_config(self, config):
        cfg = super().validate_config(config)
        if cfg.get("rows", 1) < 1:
            raise DomainError("rows باید مثبت باشد.", code="invalid_config")
        return cfg


@FieldRegistry.register
class NumberHandler(BaseFieldHandler):
    type = "number"
    config_schema = {"min": float, "max": float, "step": float, "is_integer": bool, "unit": str}
    aggregation = "numeric"

    def validate_config(self, config):
        cfg = super().validate_config(config)
        for key in ("min", "max", "step"):
            if key in cfg and not math.isfinite(float(cfg[key])):
                raise DomainError(f"{key} باید عدد متناهی باشد.", code="invalid_config")
        if "min" in cfg and "max" in cfg and cfg["min"] > cfg["max"]:
            raise DomainError("min نباید از max بیشتر باشد.", code="invalid_config")
        if "step" in cfg and cfg["step"] <= 0:
            raise DomainError("step باید مثبت باشد.", code="invalid_config")
        return cfg

    def validate_answer(self, field, raw):
        if isinstance(raw, bool) or isinstance(raw, (dict, list, tuple, set)):
            raise DomainError(f"«{field.label}» باید عدد باشد.", code="invalid_number")
        try:
            num = Decimal(str(raw))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise DomainError(f"«{field.label}» باید عدد باشد.", code="invalid_number") from exc
        if not num.is_finite():
            raise DomainError(f"«{field.label}» باید عدد متناهی باشد.", code="invalid_number")

        cfg = field.config or {}
        if cfg.get("is_integer") and num % 1 != 0:
            raise DomainError(f"«{field.label}» باید عدد صحیح باشد.", code="number_not_integer")
        if "min" in cfg and num < Decimal(str(cfg["min"])):
            raise DomainError(
                f"«{field.label}» نباید کمتر از {cfg['min']} باشد.",
                code="number_min",
            )
        if "max" in cfg and num > Decimal(str(cfg["max"])):
            raise DomainError(
                f"«{field.label}» نباید بیشتر از {cfg['max']} باشد.",
                code="number_max",
            )
        if "step" in cfg:
            base = Decimal(str(cfg.get("min", 0)))
            step = Decimal(str(cfg["step"]))
            if (num - base) % step != 0:
                raise DomainError(
                    f"«{field.label}» باید با گام {cfg['step']} سازگار باشد.",
                    code="number_step",
                )
        return ParsedAnswer(value=float(num), value_number=num)


@FieldRegistry.register
class SelectHandler(BaseFieldHandler):
    type = "select"
    config_schema = {"multiple": bool, "allow_other": bool}
    requires_options = True
    aggregation = "distribution"

    def validate_answer(self, field, raw):
        cfg = field.config or {}
        multiple = bool(cfg.get("multiple", False))
        allow_other = bool(cfg.get("allow_other", False))
        if multiple:
            values = _as_string_list(field, raw)
        else:
            if not isinstance(raw, str):
                raise DomainError(f"«{field.label}» باید یک رشته باشد.", code="invalid_option")
            values = [raw]
        if len(values) != len(set(values)):
            raise DomainError("گزینه‌ها نباید تکراری باشند.", code="duplicate_option")

        valid_values = set(field.options.values_list("value", flat=True))
        unknown = set(values) - valid_values
        if unknown and not allow_other:
            raise DomainError(
                f"گزینه‌های نامعتبر: {sorted(unknown)}",
                code="invalid_option",
            )
        return ParsedAnswer(value=raw, option_values=[value for value in values if value in valid_values])


@FieldRegistry.register
class CheckboxHandler(BaseFieldHandler):
    type = "checkbox"
    config_schema = {"min_selected": int, "max_selected": int}
    requires_options = True
    aggregation = "distribution"

    def validate_config(self, config):
        cfg = super().validate_config(config)
        if cfg.get("min_selected", 0) < 0 or cfg.get("max_selected", 0) < 0:
            raise DomainError("تعداد انتخاب نمی‌تواند منفی باشد.", code="invalid_config")
        if "min_selected" in cfg and "max_selected" in cfg and cfg["min_selected"] > cfg["max_selected"]:
            raise DomainError(
                "min_selected نباید از max_selected بیشتر باشد.",
                code="invalid_config",
            )
        return cfg

    def validate_answer(self, field, raw):
        raw = _as_string_list(field, raw, error_code="invalid_checkbox")
        if len(raw) != len(set(raw)):
            raise DomainError("گزینه‌ها نباید تکراری باشند.", code="duplicate_option")

        cfg = field.config or {}
        if "min_selected" in cfg and len(raw) < cfg["min_selected"]:
            raise DomainError(
                f"حداقل {cfg['min_selected']} گزینه انتخاب کنید.",
                code="checkbox_min",
            )
        if "max_selected" in cfg and len(raw) > cfg["max_selected"]:
            raise DomainError(
                f"حداکثر {cfg['max_selected']} گزینه مجاز است.",
                code="checkbox_max",
            )

        valid_values = set(field.options.values_list("value", flat=True))
        invalid = set(raw) - valid_values
        if invalid:
            raise DomainError(
                f"گزینه‌های نامعتبر: {sorted(invalid)}",
                code="invalid_option",
            )
        return ParsedAnswer(value=raw, option_values=raw)


@FieldRegistry.register
class RatingHandler(BaseFieldHandler):
    type = "rating"
    config_schema = {"max_value": int, "allow_half": bool, "icon": str}
    aggregation = "numeric"

    def validate_config(self, config):
        cfg = super().validate_config(config)
        max_value = cfg.get("max_value", 5)
        if max_value < 1:
            raise DomainError("max_value باید حداقل ۱ باشد.", code="invalid_config")
        return cfg

    def validate_answer(self, field, raw):
        cfg = field.config or {}
        max_value = cfg.get("max_value", 5)
        if isinstance(raw, bool) or isinstance(raw, (dict, list, tuple, set)):
            raise DomainError(f"«{field.label}» نامعتبر است.", code="invalid_rating")
        try:
            num = Decimal(str(raw))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise DomainError(f"«{field.label}» نامعتبر است.", code="invalid_rating") from exc
        if not num.is_finite():
            raise DomainError(f"«{field.label}» نامعتبر است.", code="invalid_rating")
        if not (Decimal("1") <= num <= Decimal(str(max_value))):
            raise DomainError(
                f"امتیاز باید بین ۱ تا {max_value} باشد.",
                code="rating_range",
            )
        if not cfg.get("allow_half", False) and num % 1 != 0:
            raise DomainError("امتیاز اعشاری مجاز نیست.", code="rating_half_not_allowed")
        if cfg.get("allow_half", False) and (num * 2) % 1 != 0:
            raise DomainError("امتیاز باید مضرب نیم باشد.", code="rating_precision")
        return ParsedAnswer(value=float(num), value_number=num)


@FieldRegistry.register
class DateHandler(BaseFieldHandler):
    type = "date"
    config_schema = {"min_date": str, "max_date": str, "include_time": bool}
    aggregation = "timeline"

    def validate_config(self, config):
        cfg = super().validate_config(config)
        parsed_dates = {}
        for key in ("min_date", "max_date"):
            if key in cfg:
                try:
                    parsed_dates[key] = _parse_datetime(cfg[key])
                except ValueError as exc:
                    raise DomainError(f"{key} نامعتبر است.", code="invalid_config") from exc
        if "min_date" in parsed_dates and "max_date" in parsed_dates:
            if parsed_dates["min_date"] > parsed_dates["max_date"]:
                raise DomainError(
                    "min_date نباید از max_date دیرتر باشد.",
                    code="invalid_config",
                )
        return cfg

    def validate_answer(self, field, raw):
        if not isinstance(raw, str):
            raise DomainError(f"«{field.label}» باید تاریخ ISO باشد.", code="invalid_date")
        cfg = field.config or {}
        include_time = cfg.get("include_time", True)
        if not include_time and ("T" in raw or " " in raw):
            raise DomainError(
                f"«{field.label}» باید فقط تاریخ داشته باشد.",
                code="date_time_not_allowed",
            )
        try:
            parsed = _parse_datetime(raw)
        except ValueError as exc:
            raise DomainError(
                f"«{field.label}» باید تاریخ ISO باشد.",
                code="invalid_date",
            ) from exc

        if "min_date" in cfg and parsed < _parse_datetime(cfg["min_date"]):
            raise DomainError(f"«{field.label}» نباید زودتر باشد.", code="date_min")
        if "max_date" in cfg and parsed > _parse_datetime(cfg["max_date"]):
            raise DomainError(f"«{field.label}» نباید دیرتر باشد.", code="date_max")
        return ParsedAnswer(value=raw, value_date=parsed)
