from marshmallow import Schema, fields, validate

TOPIC_CHOICES = ["parent-enquiry", "billing", "technical", "general", "partnership"]


class ContactMessageSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=30))
    topic = fields.Str(required=False, load_default="general", validate=validate.OneOf(TOPIC_CHOICES))
    message = fields.Str(required=True, validate=validate.Length(min=10, max=4000))


class ContactUpdateSchema(Schema):
    status = fields.Str(required=False, validate=validate.OneOf(["new", "read", "responded", "archived"]))
    admin_notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=4000))
