"""
مالک: روزبه (پیش از شروع کار علی)
TODO:
  - TargetType(TextChoices)       form | process
  - VisitCounter                  target_type، object_id، date، count
        unique_together = ("target_type", "object_id", "date")
  - Period(TextChoices)           weekly | monthly
  - Delivery(TextChoices)         email | webhook
  - ReportSchedule(TimeStampedModel)
        owner، target_type (blank=همه)، object_id (nullable)، period، delivery،
        email، webhook_url، secret (برای HMAC)، last_run_at، is_active
  - ReportDelivery(TimeStampedModel)
        schedule، is_success، status_code، error   (لاگ ارسال‌ها)
"""
