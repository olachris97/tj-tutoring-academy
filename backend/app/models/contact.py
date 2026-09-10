from app.core.security import gen_id
from app.extensions import db
from app.models.base import TimestampMixin

CONTACT_STATUSES = ("new", "read", "responded", "archived")


class ContactMessage(db.Model, TimestampMixin):
    __tablename__ = "contact_messages"
    __table_args__ = (
        db.CheckConstraint("status IN ('new','read','responded','archived')", name="ck_contact_status"),
        db.Index("ix_contact_status_created", "status", "created_at"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    topic = db.Column(db.String(60))  # e.g. "parent-enquiry", "general", "billing"
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="new")
    admin_notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "topic": self.topic,
            "message": self.message,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
