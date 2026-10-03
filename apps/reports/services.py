from django.core.cache import cache
from django.db.models import Avg, Count, Max, Min, Sum
from django.db.models.functions import TruncDay

from apps.core.cache import form_report_key, process_report_key
from apps.forms.fields.base import FieldRegistry
from apps.forms.models import Answer, Field

from .models import TargetType, VisitCounter  # noqa: F401



def aggregate_field(field: Field) -> dict:
    spec = FieldRegistry.get(field.type).aggregate_spec(field)
    qs = Answer.objects.filter(field=field)

    if spec["type"] == "numeric":
        stats = qs.aggregate(count=Count("id"), avg=Avg("value_number"), min=Min("value_number"),
                              max=Max("value_number"), total=Sum("value_number"))
        return {"field_id": field.id, "label": field.label, "type": field.type, **stats}

    if spec["type"] == "distribution":
        rows = (
            qs.values("selected_options__option__value", "selected_options__option__label")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        rows = [r for r in rows if r["selected_options__option__value"] is not None]
        total = sum(r["count"] for r in rows) or 1
        return {
            "field_id": field.id, "label": field.label, "type": field.type,
            "distribution": [
                {"value": r["selected_options__option__value"], "label": r["selected_options__option__label"],
                 "count": r["count"], "percent": round(r["count"] * 100 / total, 2)}
                for r in rows
            ],
        }

    if spec["type"] == "timeline":
        rows = (
            qs.exclude(value_date__isnull=True)
            .annotate(day=TruncDay("value_date"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return {"field_id": field.id, "label": field.label, "type": field.type,
                "timeline": [{"date": r["day"].date().isoformat(), "count": r["count"]} for r in rows]}

    return {"field_id": field.id, "label": field.label, "type": field.type,
            "count": qs.count(), "sample": list(qs.exclude(value_text="").values_list("value_text", flat=True)[:20])}


def form_report(form) -> dict:
    cache_key = form_report_key(form.id)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    from django.conf import settings

    data = {
        "form_id": form.id,
        "title": form.title,
        "visits": visit_count(TargetType.FORM, form.id),
        "submissions": form.submissions.filter(is_complete=True).count(),
        "fields": [aggregate_field(f) for f in form.fields.all()],
    }
    cache.set(cache_key, data, settings.CACHE_TTL_REPORT)
    return data


def process_report(process) -> dict:
    cache_key = process_report_key(process.id)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    from django.conf import settings

    data = {
        "process_id": process.id,
        "title": process.title,
        "visits": visit_count(TargetType.PROCESS, process.id),
        "runs": process.runs.count(),
        "completed_runs": process.runs.filter(status="completed").count(),
        "steps": [form_report(step.form) for step in process.steps.select_related("form")],
    }
    cache.set(cache_key, data, settings.CACHE_TTL_REPORT)
    return data


def visit_count(target_type: str, object_id: int) -> int:
    return (
        VisitCounter.objects.filter(target_type=target_type, object_id=object_id).aggregate(total=Sum("count"))[
            "total"
        ]
        or 0
    )
