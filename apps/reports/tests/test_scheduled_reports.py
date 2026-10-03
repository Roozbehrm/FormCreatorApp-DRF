import hashlib
import hmac
from unittest.mock import Mock, patch

import pytest
from celery.exceptions import Retry
from requests import Timeout

from apps.reports.models import Delivery, Period, ReportDelivery, ReportSchedule
from apps.reports.tasks import deliver_report, dispatch_due_schedules


@pytest.mark.django_db
def test_only_due_schedules_dispatch(user, form):
    due = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        period=Period.WEEKLY,
        delivery=Delivery.EMAIL,
    )
    future = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        period=Period.WEEKLY,
        delivery=Delivery.EMAIL,
    )
    from django.utils import timezone
    future.last_run_at = timezone.now()
    future.save(update_fields=["last_run_at"])
    with patch("apps.reports.tasks.deliver_report.delay") as queued:
        count = dispatch_due_schedules()
    assert count == 1
    queued.assert_called_once_with(due.id)


@pytest.mark.django_db
def test_webhook_signature_and_delivery_log(user, form):
    schedule = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        delivery=Delivery.WEBHOOK,
        webhook_url="https://example.com/hook",
        secret="secret",
    )
    captured = {}
    response = Mock(status_code=200)
    response.raise_for_status.return_value = None
    def fake_post(url, data, headers, timeout, allow_redirects):
        captured.update({"url": url, "data": data, "headers": headers, "timeout": timeout, "allow_redirects": allow_redirects})
        return response
    with patch("apps.reports.tasks.requests.post", side_effect=fake_post):
        deliver_report.run(schedule.id)
    body = captured["data"]
    expected = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    assert captured["headers"]["X-FormFlow-Signature"] == f"sha256={expected}"
    assert captured["allow_redirects"] is False
    assert ReportDelivery.objects.filter(schedule=schedule, is_success=True).exists()


@pytest.mark.django_db
def test_transient_webhook_failure_is_logged_and_retried(user, form):
    schedule = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        delivery=Delivery.WEBHOOK,
        webhook_url="https://example.com/hook",
        secret="secret",
    )

    with patch("apps.reports.tasks.requests.post", side_effect=Timeout("network timeout")):
        with patch.object(deliver_report, "retry", side_effect=Retry("retry")) as retry:
            with pytest.raises(Retry):
                deliver_report.run(schedule.id)

    retry.assert_called_once()
    delivery = ReportDelivery.objects.get(schedule=schedule)
    assert delivery.is_success is False
    assert "network timeout" in delivery.error


@pytest.mark.django_db
def test_private_webhook_target_is_rejected(user, form):
    schedule = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        delivery=Delivery.WEBHOOK,
        webhook_url="http://127.0.0.1/internal",
        secret="secret",
    )
    with pytest.raises(ValueError, match="public IP"):
        deliver_report.run(schedule.id)


@pytest.mark.django_db
def test_google_or_internal_dns_webhook_is_rejected(user, form):
    schedule = ReportSchedule.objects.create(
        owner=user,
        target_type="form",
        object_id=form.id,
        delivery=Delivery.WEBHOOK,
        webhook_url="http://localhost:8000/internal",
        secret="secret",
    )
    with pytest.raises(ValueError):
        deliver_report.run(schedule.id)
