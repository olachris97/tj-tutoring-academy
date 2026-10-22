from app.core.errors import NotFoundApiError
from app.extensions import db
from app.models import TeacherApplication, log_action
from app.services.mailer import notify_new_application


class ApplicationService:
    def submit(self, data):
        application = TeacherApplication(
            full_name=data["full_name"].strip(),
            email=data["email"].strip().lower(),
            phone=data["phone"].strip(),
            subjects=data["subjects"].strip(),
            levels=data.get("levels"),
            qualification=data["qualification"].strip(),
            years_experience=data.get("years_experience", 0),
            availability=data.get("availability"),
            location=data.get("location"),
            cover_note=data.get("cover_note"),
            resume_url=data.get("resume_url"),
            status="submitted",
        )
        db.session.add(application)
        db.session.commit()
        notify_new_application(application)
        return application

    def list(self, status=None, page=1, per_page=20):
        query = TeacherApplication.query
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(TeacherApplication.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get(self, application_id):
        application = TeacherApplication.query.get(application_id)
        if not application:
            raise NotFoundApiError("Application not found.")
        return application

    def update(self, admin, application_id, data):
        application = self.get(application_id)
        if "status" in data:
            application.status = data["status"]
        if "admin_notes" in data:
            application.admin_notes = data["admin_notes"]
        log_action(admin.id, "application.update", "TeacherApplication", application.id)
        db.session.commit()
        return application

    def delete(self, admin, application_id):
        application = self.get(application_id)
        log_action(admin.id, "application.delete", "TeacherApplication", application.id)
        db.session.delete(application)
        db.session.commit()


application_service = ApplicationService()
