from dataclasses import dataclass, field as dc_field
from typing import Any

from apps.core.exceptions import DomainError


@dataclass
class ParsedAnswer:
    value: Any = None
    value_number: Any = None
    value_date: Any = None
    value_text: str = ""
    option_values: list[str] = dc_field(default_factory=list)


class BaseFieldHandler:
    type = ""
    config_schema = {}
    requires_options = False
    aggregation = "list"

    def validate_config(self, config: dict) -> dict:
        if not isinstance(config, dict):
            raise DomainError("تنظیمات فیلد باید شیء باشد.", code="invalid_config")
        unknown = set(config) - set(self.config_schema)
        if unknown:
            raise DomainError(f"کلیدهای ناشناخته در تنظیمات: {sorted(unknown)}", code="invalid_config")
        for key, value in config.items():
            expected = self.config_schema[key]
            if expected is int and (isinstance(value, bool) or not isinstance(value, int)):
                raise DomainError(f"نوع {key} نامعتبر است.", code="invalid_config")
            if expected is float and (isinstance(value, bool) or not isinstance(value, (int, float))):
                raise DomainError(f"نوع {key} نامعتبر است.", code="invalid_config")
            if expected is bool and not isinstance(value, bool):
                raise DomainError(f"نوع {key} نامعتبر است.", code="invalid_config")
            if expected is str and not isinstance(value, str):
                raise DomainError(f"نوع {key} نامعتبر است.", code="invalid_config")
        return config

    def validate_answer(self, field, raw) -> ParsedAnswer:
        raise NotImplementedError

    def aggregate_spec(self, field) -> dict:
        return {"type": self.aggregation}


class FieldRegistry:
    _handlers = {}

    @classmethod
    def register(cls, handler_cls):
        cls._handlers[handler_cls.type] = handler_cls()
        return handler_cls

    @classmethod
    def get(cls, field_type: str) -> BaseFieldHandler:
        try:
            return cls._handlers[field_type]
        except KeyError as exc:
            raise DomainError(f"نوع فیلد پشتیبانی نمی‌شود: {field_type}", code="unknown_field_type") from exc

    @classmethod
    def all(cls):
        return dict(cls._handlers)
