"""
مالک: روزبه
TODO:
  - DomainError(Exception)     پایه خطاهای منطق کسب‌وکار: message, code="domain_error", status_code=400
  - StepLocked(DomainError)    code="step_locked", status_code=409
  - AccessDenied(DomainError)  code="access_denied", status_code=403
  - api_exception_handler(exc, context)
        قالب یکدست خروجی خطا: {"error": {"code": ..., "message"/"detail": ...}}
        در settings.REST_FRAMEWORK["EXCEPTION_HANDLER"] ثبت می‌شود.
"""
