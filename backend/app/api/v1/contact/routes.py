from flask import Blueprint, request

from app.extensions import limiter
from app.schemas.contact_schemas import ContactMessageSchema
from app.services.contact_service import contact_service

bp = Blueprint("contact_v1", __name__)

contact_schema = ContactMessageSchema()


@bp.post("")
@limiter.limit("5 per minute")
def submit_contact_message():
    data = contact_schema.load(request.get_json(silent=True) or {})
    message = contact_service.submit(data)
    return {"submitted": True, "id": message.id}, 201
