"""مالک: علی"""
from celery import shared_task


@shared_task
def flush_visit_counters() -> int:
    """انتقال شمارنده‌های بازدید از Redis به VisitCounter. TODO"""
    return 0


@shared_task
def dispatch_due_schedules() -> int:
    """پیدا کردن ReportScheduleهای سررسیدشده و صف کردن ارسال. TODO"""
    return 0


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_report(self, schedule_id: int) -> None:
    """ساخت گزارش + ارسال ایمیل یا POST به webhook با امضای HMAC. TODO"""
