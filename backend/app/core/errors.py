class ApiError(Exception):
    status_code = 400
    error_code = "bad_request"

    def __init__(self, message, status_code=None, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details

    def to_dict(self):
        body = {"error": {"code": self.error_code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return body


class ValidationApiError(ApiError):
    status_code = 422
    error_code = "validation_error"


class NotFoundApiError(ApiError):
    status_code = 404
    error_code = "not_found"


class UnauthorizedApiError(ApiError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenApiError(ApiError):
    status_code = 403
    error_code = "forbidden"


class ConflictApiError(ApiError):
    status_code = 409
    error_code = "conflict"
