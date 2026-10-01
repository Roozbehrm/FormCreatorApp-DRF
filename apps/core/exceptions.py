from rest_framework.views import exception_handler


class DomainError(Exception):
    code = "domain_error"
    status_code = 400

    def __init__(self, message: str, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code


class StepLocked(DomainError):
    code = "step_locked"
    status_code = 409


class AccessDenied(DomainError):
    code = "access_denied"
    status_code = 403


class NotFoundDomainError(DomainError):
    code = "not_found"
    status_code = 404


def api_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        from rest_framework.response import Response

        return Response({"error": {"code": exc.code, "message": exc.message}}, status=exc.status_code)

    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": {"code": "invalid", "detail": response.data}}
    return response
