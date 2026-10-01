from django.core.cache import cache


def form_schema_key(form_uuid) -> str:
    return f"form:schema:{form_uuid}"


def form_report_key(form_id: int) -> str:
    return f"form:report:{form_id}"


def process_report_key(process_id: int) -> str:
    return f"process:report:{process_id}"


def invalidate_form(form_id: int, form_uuid) -> None:
    cache.delete_many([form_schema_key(form_uuid), form_report_key(form_id)])


def invalidate_process(process_id: int) -> None:
    cache.delete(process_report_key(process_id))
