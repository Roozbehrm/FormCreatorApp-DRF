"""
مالک: مهیار
TODO: Category(TimeStampedModel)
      owner (FK به User)، title، parent (self FK، nullable — برای درخت دسته‌ها)، color
      unique_together = ("owner", "title", "parent")

پیش‌نیاز: apps/core/models.py (TimeStampedModel) باید قبلش تمام شده باشد.
"""
