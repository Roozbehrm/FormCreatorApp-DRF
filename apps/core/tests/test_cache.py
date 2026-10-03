from django.core.cache import cache

from apps.core.cache import (
    form_report_key,
    form_schema_key,
    invalidate_form,
    invalidate_process,
    process_report_key,
)


def test_cache_keys_are_stable():
    assert form_schema_key("form-uuid") == "form:schema:form-uuid"
    assert form_report_key(12) == "form:report:12"
    assert process_report_key(34) == "process:report:34"


def test_invalidate_form_clears_schema_and_report_keys():
    cache.set(form_schema_key("form-uuid"), {"schema": True})
    cache.set(form_report_key(12), {"report": True})

    invalidate_form(12, "form-uuid")

    assert cache.get(form_schema_key("form-uuid")) is None
    assert cache.get(form_report_key(12)) is None


def test_invalidate_process_clears_process_report_key():
    cache.set(process_report_key(34), {"report": True})

    invalidate_process(34)

    assert cache.get(process_report_key(34)) is None
