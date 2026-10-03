import hashlib
import hmac
import ipaddress
import json
import smtplib
import socket
from datetime import date
from urllib.parse import urlparse

import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.core.cache import visit_index_key

from .models import Delivery, ReportDelivery, ReportSchedule, TargetType, VisitCounter
from .services import form_report, process_report, _redis_client


def _parse_visit_key(key: str):
    parts = key.split(":")
    if len(parts) != 4 or parts[0] != "visit":
        return None
    _, target_type, object_id, date_text = parts
    if target_type not in TargetType.values:
        return None
    try:
        object_id = int(object_id)
        date.fromisoformat(date_text)
    except (TypeError, ValueError):
        return None
    return target_type, object_id, date_text


def _get_pending_visit_keys():
    redis_client = _redis_client()
    if redis_client is not None:
        raw_keys = redis_client.smembers(cache.make_key(visit_index_key()))
        return {item.decode() if isinstance(item, bytes) else str(item) for item in raw_keys}
    return set(cache.get(visit_index_key()) or [])


def _discard_pending_visit_key(key: str) -> None:
    redis_client = _redis_client()
    if redis_client is not None:
        redis_client.srem(cache.make_key(visit_index_key()), key)
    else:
        keys = set(cache.get(visit_index_key()) or [])
        keys.discard(key)
        cache.set(visit_index_key(), list(keys), settings.VISIT_PENDING_TTL_SECONDS)


def _drain_visit_count(key: str) -> int:
    redis_client = _redis_client()
    if redis_client is None:
        count = int(cache.get(key) or 0)
        if count > 0:
            cache.incr(key, -count)
        return count

    redis_key = cache.make_key(key)
    raw = redis_client.getset(redis_key, 0)
    if raw is None:
        return 0
    # GETSET clears the TTL, so restore it after atomically taking the count.
    redis_client.expire(redis_key, settings.VISIT_PENDING_TTL_SECONDS)
    return int(raw)


def _restore_visit_count(key: str, count: int) -> None:
    if count <= 0:
        return
    cache.incr(key, count)
    cache.touch(key, timeout=settings.VISIT_PENDING_TTL_SECONDS)


def _flush_visit_counters_impl() -> int:
    flushed = 0
    keys = _get_pending_visit_keys()

    for key in keys:
        parsed = _parse_visit_key(key)
        if not parsed:
            cache.delete(key)
            _discard_pending_visit_key(key)
            continue

        target_type, object_id, date_text = parsed
        count = _drain_visit_count(key)
        if count <= 0:
            if not cache.get(key):
                _discard_pending_visit_key(key)
            continue

        try:
            with transaction.atomic():
                counter, _ = VisitCounter.objects.select_for_update().get_or_create(
                    target_type=target_type,
                    object_id=object_id,
                    date=date.fromisoformat(date_text),
                    defaults={"count": 0},
                )
                counter.count += count
                counter.save(update_fields=["count"])
        except Exception:
            _restore_visit_count(key, count)
            raise

        flushed += count
        if int(cache.get(key) or 0) <= 0:
            cache.delete(key)
            _discard_pending_visit_key(key)

    if _redis_client() is None:
        remaining = set(cache.get(visit_index_key()) or [])
        cache.set(
            visit_index_key(),
            list(remaining),
            settings.VISIT_PENDING_TTL_SECONDS,
        )
    return flushed


@shared_task
def flush_visit_counters() -> int:
    lock_factory = getattr(cache, "lock", None)
    if lock_factory is not None:
        with lock_factory("formflow:visit-flush-lock", timeout=300, blocking_timeout=5):
            return _flush_visit_counters_impl()
    return _flush_visit_counters_impl()


@shared_task
def dispatch_due_schedules() -> int:
    now = timezone.now()
    queued = 0
    ids = list(
        ReportSchedule.objects.filter(is_active=True)
        .values_list("id", flat=True)
    )

    for schedule_id in ids:
        with transaction.atomic():
            schedule = (
                ReportSchedule.objects
                .select_for_update()
                .select_related("owner")
                .get(id=schedule_id)
            )
            if not schedule.is_due(now):
                continue
            schedule.last_run_at = now
            schedule.save(update_fields=["last_run_at", "updated_at"])

        deliver_report.delay(schedule_id)
        queued += 1

    return queued


def _report_for_schedule(schedule):
    if not schedule.target_type or not schedule.object_id:
        raise ValueError("Schedule target is not configured")
    if schedule.target_type == TargetType.FORM:
        from apps.forms.models import Form

        form = Form.objects.get(id=schedule.object_id, owner=schedule.owner)
        return form_report(form)
    if schedule.target_type == TargetType.PROCESS:
        from apps.processes.models import Process

        process = Process.objects.get(id=schedule.object_id, owner=schedule.owner)
        return process_report(process)
    raise ValueError("Unsupported target type")


def _deliver_email(schedule, payload):
    recipient = schedule.email or schedule.owner.email
    if not recipient:
        raise ValueError("No email recipient configured")
    send_mail(
        subject=f"FormFlow report — {schedule.target_type or 'overview'}",
        message=json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
    return None


def _resolve_public_ips(hostname: str):
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as exc:
        raise ValueError("Webhook hostname could not be resolved") from exc

    if not addresses:
        raise ValueError("Webhook hostname could not be resolved")

    for value in addresses:
        try:
            ip = ipaddress.ip_address(value)
        except ValueError as exc:
            raise ValueError("Webhook hostname resolved to an invalid IP") from exc
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError("Webhook URL must resolve to a public IP address")


def _validate_webhook_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Webhook URL must use http or https")
    if parsed.username or parsed.password:
        raise ValueError("Webhook URL must not contain credentials")
    if not parsed.hostname:
        raise ValueError("Webhook URL must include a hostname")

    try:
        literal_ip = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if (
            literal_ip.is_private
            or literal_ip.is_loopback
            or literal_ip.is_link_local
            or literal_ip.is_reserved
            or literal_ip.is_multicast
            or literal_ip.is_unspecified
        ):
            raise ValueError("Webhook URL must resolve to a public IP address")
    else:
        _resolve_public_ips(parsed.hostname)

    return raw_url


def _deliver_webhook(schedule, payload):
    if not schedule.webhook_url:
        raise ValueError("Webhook URL is not configured")
    if not schedule.secret:
        raise ValueError("Webhook secret is not configured")

    url = _validate_webhook_url(schedule.webhook_url)
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    signature = hmac.new(
        schedule.secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    response = requests.post(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-FormFlow-Signature": f"sha256={signature}",
        },
        timeout=settings.REPORT_WEBHOOK_TIMEOUT_SECONDS,
        allow_redirects=False,
    )
    response.raise_for_status()
    return response.status_code


def _is_transient_delivery_error(exc):
    return isinstance(
        exc,
        (
            requests.RequestException,
            OSError,
            TimeoutError,
            smtplib.SMTPException,
            ConnectionError,
        ),
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_report(self, schedule_id: int) -> None:
    schedule = ReportSchedule.objects.select_related("owner").get(id=schedule_id)
    delivery = ReportDelivery.objects.create(schedule=schedule)
    try:
        payload = _report_for_schedule(schedule)
        if schedule.delivery == Delivery.EMAIL:
            status_code = _deliver_email(schedule, payload)
        elif schedule.delivery == Delivery.WEBHOOK:
            status_code = _deliver_webhook(schedule, payload)
        else:
            raise ValueError("Unsupported delivery")
    except Exception as exc:
        delivery.is_success = False
        delivery.error = str(exc)[:1000]
        delivery.status_code = getattr(
            getattr(exc, "response", None),
            "status_code",
            None,
        )
        delivery.save(update_fields=["is_success", "error", "status_code", "updated_at"])
        if _is_transient_delivery_error(exc):
            raise self.retry(exc=exc)
        raise

    delivery.is_success = True
    delivery.status_code = status_code
    delivery.save(update_fields=["is_success", "status_code", "updated_at"])
