from marshmallow import Schema, fields, validate

STATUS_CHOICES = ["submitted", "reviewing", "shortlisted", "rejected", "hired"]


class TeacherApplicationSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=6, max=30))
    subjects = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    levels = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
    qualification = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    years_experience = fields.Int(required=False, load_default=0, validate=validate.Range(min=0, max=60))
    availability = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=120))
    cover_note = fields.Str(required=False, allow_none=True, validate=validate.Length(max=4000))
    resume_url = fields.Url(required=False, allow_none=True)


class ApplicationUpdateSchema(Schema):
    status = fields.Str(required=False, validate=validate.OneOf(STATUS_CHOICES))
    admin_notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=4000))
