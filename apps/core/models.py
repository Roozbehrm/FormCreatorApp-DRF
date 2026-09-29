"""
مالک: روزبه — پیش‌نیاز همه اپ‌های دیگر، باید زودتر از بقیه تمام شود.
TODO:
  - TimeStampedModel(models.Model)   created_at (auto_now_add), updated_at (auto_now)
  - UUIDModel(models.Model)          uuid = UUIDField(default=uuid4, unique=True)  — برای لینک یکتا
  - Visibility(TextChoices)          PUBLIC="public" | PRIVATE="private"
  - ShareableModel(TimeStampedModel, UUIDModel)
        title, description, visibility, access_password (هش‌شده), is_active
        property is_private

نکته: accounts.OTPRequestLog، categories.Category و همه مدل‌های forms/processes/reports
از این کلاس‌ها ارث می‌برند — تا این فایل تمام نشود بقیه اپ‌ها هم قابل اجرا نیستند.
"""
