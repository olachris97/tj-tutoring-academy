from app.api.v1.auth.routes import bp as auth_bp
from app.api.v1.contact.routes import bp as contact_bp
from app.api.v1.applications.routes import bp as applications_bp
from app.api.v1.admin.routes import bp as admin_bp

_MOUNTS = [
    (auth_bp, "/auth", "auth"),
    (contact_bp, "/contact", "contact"),
    (applications_bp, "/applications", "applications"),
    (admin_bp, "/admin", "admin"),
]


def register_v1(app):
    for blueprint, url_prefix, name in _MOUNTS:
        app.register_blueprint(blueprint, url_prefix=f"/api/v1{url_prefix}", name=name)
