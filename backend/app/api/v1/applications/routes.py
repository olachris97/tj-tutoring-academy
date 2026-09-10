from flask import Blueprint, request

from app.extensions import limiter
from app.schemas.application_schemas import TeacherApplicationSchema
from app.services.application_service import application_service

bp = Blueprint("applications_v1", __name__)

application_schema = TeacherApplicationSchema()


@bp.post("")
@limiter.limit("5 per minute")
def submit_application():
    data = application_schema.load(request.get_json(silent=True) or {})
    application = application_service.submit(data)
    return {"submitted": True, "id": application.id}, 201
