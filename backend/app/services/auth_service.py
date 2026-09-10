from datetime import datetime, timezone

from app.core.errors import UnauthorizedApiError, ValidationApiError
from app.core.security import decode_token, issue_access_token, issue_refresh_token
from app.extensions import db
from app.models import AdminUser, RefreshToken, log_action

MAX_FAILED_ATTEMPTS = 8


class AuthService:
    def login(self, email, password):
        admin = AdminUser.query.filter_by(email=email.lower().strip()).first()
        if not admin or not admin.check_password(password):
            if admin:
                admin.failed_login_attempts += 1
                if admin.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    admin.status = "disabled"
                db.session.commit()
            raise UnauthorizedApiError("Incorrect email or password.")

        if admin.status != "active":
            raise UnauthorizedApiError("This account has been disabled. Contact another administrator.")

        admin.failed_login_attempts = 0
        admin.last_login_at = datetime.utcnow()
        log_action(admin.id, "auth.login", "AdminUser", admin.id)
        db.session.commit()

        return self._issue_tokens(admin)

    def refresh(self, refresh_token):
        payload = decode_token(refresh_token, expected_type="refresh")
        stored = RefreshToken.query.get(payload["jti"])
        if not stored or stored.revoked_at is not None:
            raise UnauthorizedApiError("Session has been revoked. Please log in again.")
        if stored.expires_at < datetime.utcnow():
            raise UnauthorizedApiError("Session expired. Please log in again.")

        admin = AdminUser.query.get(payload["sub"])
        if not admin or admin.status != "active":
            raise UnauthorizedApiError("Account is no longer active.")

        # Rotate: revoke the used refresh token, issue a new pair
        stored.revoked_at = datetime.utcnow()
        db.session.commit()
        return self._issue_tokens(admin)

    def logout(self, refresh_token):
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except UnauthorizedApiError:
            return  # already invalid/expired — nothing to revoke
        stored = RefreshToken.query.get(payload["jti"])
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.utcnow()
            db.session.commit()

    def change_password(self, admin, current_password, new_password):
        if not admin.check_password(current_password):
            raise ValidationApiError("Current password is incorrect.")
        admin.set_password(new_password)
        log_action(admin.id, "auth.change_password", "AdminUser", admin.id)
        db.session.commit()

    def _issue_tokens(self, admin):
        access_token = issue_access_token(admin.id)
        refresh_token, jti, expires_at = issue_refresh_token(admin.id)
        db.session.add(RefreshToken(id=jti, admin_id=admin.id, expires_at=expires_at.replace(tzinfo=None)))
        db.session.commit()
        return access_token, refresh_token, admin


auth_service = AuthService()
