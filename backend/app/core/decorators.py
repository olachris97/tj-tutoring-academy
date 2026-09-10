from functools import wraps

from flask import g, request

from app.core.errors import UnauthorizedApiError
from app.core.security import decode_token
from app.models import AdminUser


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return None


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            raise UnauthorizedApiError("Missing authentication token.")
        payload = decode_token(token, expected_type="access")

        admin = AdminUser.query.get(payload["sub"])
        if not admin or admin.status != "active":
            raise UnauthorizedApiError("Account is no longer active.")

        g.current_admin = admin
        return fn(*args, **kwargs)

    return wrapper


def current_admin():
    return g.current_admin
