from app.core.security import gen_id, hash_password, verify_password
from app.extensions import db
from app.models.base import TimestampMixin


class AdminUser(db.Model, TimestampMixin):
    __tablename__ = "admin_users"
    __table_args__ = (
        db.CheckConstraint("status IN ('active','disabled')", name="ck_admin_users_status"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, raw_password):
        self.password_hash = hash_password(raw_password)

    def check_password(self, raw_password):
        return verify_password(raw_password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "status": self.status,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RefreshToken(db.Model, TimestampMixin):
    """We store refresh tokens by id (jti) so a logout / password change can
    revoke them server-side — a bare JWT can't be invalidated on its own."""

    __tablename__ = "refresh_tokens"

    id = db.Column(db.String(36), primary_key=True)  # the token's jti
    admin_id = db.Column(db.String(36), db.ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)
