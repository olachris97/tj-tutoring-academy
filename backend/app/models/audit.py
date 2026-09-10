from app.core.security import gen_id
from app.extensions import db
from app.models.base import TimestampMixin


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (db.Index("ix_audit_entity", "entity_type", "entity_id"),)

    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    admin_id = db.Column(db.String(36), db.ForeignKey("admin_users.id", ondelete="SET NULL"))
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(60), nullable=False)
    entity_id = db.Column(db.String(36))

    def to_dict(self):
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def log_action(admin_id, action, entity_type, entity_id=None):
    entry = AuditLog(admin_id=admin_id, action=action, entity_type=entity_type, entity_id=entity_id)
    db.session.add(entry)
    return entry
