from app import create_app
from app.extensions import db
from app.models import AdminUser
import os

app = create_app()

with app.app_context():
    email = os.environ.get(
        "ADMIN_EMAIL",
        "admin@tjtutoring.academy"
    )

    password = os.environ.get(
        "ADMIN_PASSWORD"
    )

    if not password:
        raise RuntimeError(
            "ADMIN_PASSWORD environment variable is required"
        )

    admin = AdminUser.query.filter_by(email=email.lower().strip()).first()

    if admin:
        print(f"Admin found: {email}")
        admin.set_password(password)
        admin.status = "active"
        admin.failed_login_attempts = 0
        print("Admin password has been reset.")
    else:
        admin = AdminUser(
            email=email.lower().strip(),
            full_name="TJ Tutoring Admin",
            status="active",
            failed_login_attempts=0,
        )
        admin.set_password(password)
        db.session.add(admin)
        print(f"Admin created: {email}")

    db.session.commit()

    print("Admin setup completed successfully.")