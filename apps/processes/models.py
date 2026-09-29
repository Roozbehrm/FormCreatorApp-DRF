"""
مالک: روزبه
TODO:
  - ProcessType(TextChoices)     linear | free
  - Process(ShareableModel)      owner، category (FK nullable)، type
  - ProcessStep                  process، form (FK PROTECT)، order، is_required
        unique_together = ("process", "form")
  - RunStatus(TextChoices)       in_progress | completed
  - ProcessRun(TimeStampedModel) process، respondent (FK nullable)، session_key، status، completed_at
  - StepCompletion                run، step، submission (OneToOne به forms.Submission)
        unique_together = ("run", "step")

پیش‌نیاز: apps/core/models.py و apps/forms/models.py باید قبلش تمام شده باشند.
"""
