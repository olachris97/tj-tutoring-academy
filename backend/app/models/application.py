from app.core.security import gen_id
from app.extensions import db
from app.models.base import TimestampMixin

APPLICATION_STATUSES = ("submitted", "reviewing", "shortlisted", "rejected", "hired")


class TeacherApplication(db.Model, TimestampMixin):
    __tablename__ = "teacher_applications"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('submitted','reviewing','shortlisted','rejected','hired')",
            name="ck_application_status",
        ),
        db.Index("ix_application_status_created", "status", "created_at"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)  # comma-separated, e.g. "Mathematics, Physics"
    levels = db.Column(db.String(255))  # e.g. "KS2 SATs, GCSE, IGCSE"
    qualification = db.Column(db.String(255), nullable=False)
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    availability = db.Column(db.String(255))  # e.g. "Weekday evenings, UK time"
    location = db.Column(db.String(120))
    cover_note = db.Column(db.Text)
    resume_url = db.Column(db.String(500))  # link to an externally hosted CV, not a file upload
    status = db.Column(db.String(20), nullable=False, default="submitted")
    admin_notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "subjects": self.subjects,
            "levels": self.levels,
            "qualification": self.qualification,
            "years_experience": self.years_experience,
            "availability": self.availability,
            "location": self.location,
            "cover_note": self.cover_note,
            "resume_url": self.resume_url,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
