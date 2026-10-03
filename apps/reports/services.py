from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.cache import form_report_key, process_report_key, visit_index_key
from apps.forms.fields.base import FieldRegistry
from apps.forms.models import Answer, Field

from .models import TargetType, VisitCounter

_VALUE_NUMBER_QUANT = Decimal(1).scaleb(-Answer._meta.get_field("value_number").decimal_places)  # Decimal("0.0001")


def _quantize(value):
    """Quantizes a numeric value to the precision defined in the Answer model."""
    return None if value is None else Decimal(value).quantize(_VALUE_NUMBER_QUANT)


def _redis_client():
    
    try:
        return cache.client.get_client(write=True)
    except AttributeError:
        return None


def record_visit(target_type: str, object_id: int) -> int:
    if target_type not in TargetType.values:
        raise ValueError(f"Unsupported visit target type: {target_type}")

    visit_key = f"visit:{target_type}:{int(object_id)}:{timezone.localdate().isoformat()}"
    cache.add(visit_key, 0, timeout=settings.VISIT_PENDING_TTL_SECONDS)
    count = cache.incr(visit_key)

    index_key = visit_index_key()
    indexed_keys = set(cache.get(index_key) or [])
    indexed_keys.add(visit_key)
    cache.set(index_key, list(indexed_keys), timeout=settings.VISIT_PENDING_TTL_SECONDS)
    return count


def aggregate_field(field: Field) -> dict:
    spec = FieldRegistry.get(field.type).aggregate_spec(field)
    qs = Answer.objects.filter(field=field, submission__is_complete=True)

    if spec["type"] == "numeric":
        stats = qs.aggregate(count=Count("id"), avg=Avg("value_number"), min=Min("value_number"),
                              max=Max("value_number"), total=Sum("value_number"))
        for key in ("avg", "min", "max", "total"):
            stats[key] = _quantize(stats[key])
        return {"field_id": field.id, "label": field.label, "type": field.type, **stats}

    if spec["type"] == "distribution":
        rows = (
            field.options.annotate(
                count=Count(
                    "answer_links",
                    filter=Q(answer_links__answer__submission__is_complete=True),
                )
            )
            .order_by("order", "id")
        )
        total = sum(option.count for option in rows)
        return {
            "field_id": field.id, "label": field.label, "type": field.type,
            "distribution": [
                {
                    "value": option.value,
                    "label": option.label,
                    "count": option.count,
                    "percent": round(option.count * 100 / total, 2) if total else 0,
                }
                for option in rows
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


def text_answer_page(field: Field, page=1, page_size=20) -> dict:
    try:
        page_number = int(page)
        requested_page_size = int(page_size)
    except (TypeError, ValueError) as exc:
        raise ValidationError("page and page_size must be integers.") from exc

    if page_number < 1:
        raise ValidationError({"page": "page must be greater than zero."})
    if requested_page_size < 1 or requested_page_size > 100:
        raise ValidationError({"page_size": "page_size must be between 1 and 100."})

    answers = (
        Answer.objects.filter(field=field, submission__is_complete=True)
        .exclude(value_text="")
        .order_by("-submission__created_at", "-id")
    )
    paginator = Paginator(answers, requested_page_size)
    page_obj = paginator.get_page(page_number)
    return {
        "field_id": field.id,
        "count": paginator.count,
        "page": page_obj.number,
        "page_size": requested_page_size,
        "total_pages": paginator.num_pages,
        "results": [
            {"id": answer.id, "value": answer.value_text, "submitted_at": answer.submission.created_at}
            for answer in page_obj.object_list.select_related("submission")
        ],
    }
