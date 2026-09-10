import uuid
from datetime import datetime, timezone

import bcrypt
import jwt
from flask import current_app

from app.core.errors import UnauthorizedApiError


def gen_id():
    return str(uuid.uuid4())


def hash_password(raw_password):
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password, password_hash):
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _encode(payload, ttl, jti=None):
    now = datetime.now(timezone.utc)
    payload = {
        **payload,
        "iat": now,
        "exp": now + ttl,
        "jti": jti or gen_id(),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token, payload["jti"], payload["exp"]


def issue_access_token(admin_id):
    token, _, _ = _encode({"sub": admin_id, "type": "access"}, current_app.config["ACCESS_TOKEN_TTL"])
    return token


def issue_refresh_token(admin_id, jti=None):
    return _encode({"sub": admin_id, "type": "refresh"}, current_app.config["REFRESH_TOKEN_TTL"], jti=jti)


def decode_token(token, expected_type=None):
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedApiError("Session expired. Please log in again.", error_code="token_expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedApiError("Invalid session token.", error_code="token_invalid")

    if expected_type and payload.get("type") != expected_type:
        raise UnauthorizedApiError("Invalid token type.", error_code="token_invalid")
    return payload
