from flask import Blueprint, request

from app.core.decorators import current_admin, require_admin
from app.core.pagination import paginated_response
from app.schemas.application_schemas import ApplicationUpdateSchema
from app.schemas.contact_schemas import ContactUpdateSchema
from app.services.application_service import application_service
from app.services.contact_service import contact_service
from app.services.dashboard_service import dashboard_service

bp = Blueprint("admin_v1", __name__)

contact_update_schema = ContactUpdateSchema()
application_update_schema = ApplicationUpdateSchema()


@bp.get("/dashboard/summary")
@require_admin
def dashboard_summary():
    return dashboard_service.summary()


# ---------------------------------------------------------------------------
# Contact messages
# ---------------------------------------------------------------------------
@bp.get("/messages")
@require_admin
def list_messages():
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = contact_service.list(status=status, page=page, per_page=per_page)
    return paginated_response(pagination, lambda m: m.to_dict())


@bp.get("/messages/<message_id>")
@require_admin
def get_message(message_id):
    message = contact_service.get(message_id)
    contact_service.mark_read_if_new(message)
    return message.to_dict()


@bp.patch("/messages/<message_id>")
@require_admin
def update_message(message_id):
    data = contact_update_schema.load(request.get_json(silent=True) or {}, partial=True)
    message = contact_service.update(current_admin(), message_id, data)
    return message.to_dict()


@bp.delete("/messages/<message_id>")
@require_admin
def delete_message(message_id):
    contact_service.delete(current_admin(), message_id)
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Teacher applications
# ---------------------------------------------------------------------------
@bp.get("/applications")
@require_admin
def list_applications():
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    pagination = application_service.list(status=status, page=page, per_page=per_page)
    return paginated_response(pagination, lambda a: a.to_dict())


@bp.get("/applications/<application_id>")
@require_admin
def get_application(application_id):
    application = application_service.get(application_id)
    return application.to_dict()


@bp.patch("/applications/<application_id>")
@require_admin
def update_application(application_id):
    data = application_update_schema.load(request.get_json(silent=True) or {}, partial=True)
    application = application_service.update(current_admin(), application_id, data)
    return application.to_dict()


@bp.delete("/applications/<application_id>")
@require_admin
def delete_application(application_id):
    application_service.delete(current_admin(), application_id)
    return {"deleted": True}
