"""
مالک: روزبه
TODO:
  - assert_step_unlocked(run, step)
        در فرایند خطی، اگر پیش‌نیازهای اجباریِ با order کمتر تکمیل نشده باشند
        apps.core.exceptions.StepLocked را بالا بینداز.
        در فرایند آزاد همیشه عبور کن.
  - complete_step(run, step, submission) -> StepCompletion
        StepCompletion بساز؛ اگر همه استپ‌های اجباری فرایند تکمیل شده باشند،
        run.status را completed کن و completed_at را ثبت کن.
"""
