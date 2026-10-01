from dataclasses import dataclass, field as dc_field
from typing import Any

from apps.core.exceptions import DomainError


@dataclass
class ParsedAnswer:
    value: Any = None
    value_number: Any = None
    value_date: Any = None
    value_text: str = ""
    option_values: list = dc_field(default_factory=list)


class BaseFieldHandler:
    type: str = ""
    config_schema: dict = {}
    requires_options: bool = False
    aggregation: str = "list"

    def validate_config(self, config: dict) -> dict:
        unknown = set(config) - set(self.config_schema)
        if unknown:
            raise DomainError(f"کلیدهای ناشناخته در تنظیمات: {sorted(unknown)}", code="invalid_config")
        return config

    def validate_answer(self, field, raw) -> ParsedAnswer:
        raise NotImplementedError

    def aggregate_spec(self, field) -> dict:
        return {"type": self.aggregation}


class FieldRegistry:
    _handlers: dict[str, BaseFieldHandler] = {}

    @classmethod
    def register(cls, handler_cls):
        cls._handlers[handler_cls.type] = handler_cls()
        return handler_cls

    @classmethod
    def get(cls, field_type: str) -> BaseFieldHandler:
        try:
            return cls._handlers[field_type]
        except KeyError:
            raise DomainError(f"نوع فیلد پشتیبانی نمی‌شود: {field_type}", code="unknown_field_type")

    @classmethod
    def all(cls) -> dict:
        return dict(cls._handlers)
