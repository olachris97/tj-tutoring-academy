from flask import Blueprint, request

from app.core.decorators import current_admin, require_admin
from app.core.errors import ValidationApiError
from app.extensions import limiter
from app.schemas.auth_schemas import ChangePasswordSchema, LoginSchema
from app.services.auth_service import auth_service

bp = Blueprint("auth_v1", __name__)

login_schema = LoginSchema()
change_password_schema = ChangePasswordSchema()


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = login_schema.load(request.get_json(silent=True) or {})
    access_token, refresh_token, admin = auth_service.login(data["email"], data["password"])
    return {"access_token": access_token, "refresh_token": refresh_token, "admin": admin.to_dict()}


@bp.post("/refresh")
@limiter.limit("30 per minute")
def refresh():
    body = request.get_json(silent=True) or {}
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise ValidationApiError("refresh_token is required.")
    access_token, new_refresh_token, admin = auth_service.refresh(refresh_token)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "admin": admin.to_dict()}


@bp.post("/logout")
def logout():
    body = request.get_json(silent=True) or {}
    refresh_token = body.get("refresh_token")
    if refresh_token:
        auth_service.logout(refresh_token)
    return {"logged_out": True}


@bp.get("/me")
@require_admin
def me():
    return current_admin().to_dict()


@bp.post("/change-password")
@require_admin
def change_password():
    data = change_password_schema.load(request.get_json(silent=True) or {})
    auth_service.change_password(current_admin(), data["current_password"], data["new_password"])
    return {"changed": True}
