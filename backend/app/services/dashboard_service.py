from datetime import datetime, timedelta

from app.models import AuditLog, ContactMessage, TeacherApplication


class DashboardService:
    def summary(self):
        since_7d = datetime.utcnow() - timedelta(days=7)

        messages = ContactMessage.query.all()
        applications = TeacherApplication.query.all()

        return {
            "messages": {
                "total": len(messages),
                "new": sum(1 for m in messages if m.status == "new"),
                "last_7_days": sum(1 for m in messages if m.created_at >= since_7d),
            },
            "applications": {
                "total": len(applications),
                "submitted": sum(1 for a in applications if a.status == "submitted"),
                "shortlisted": sum(1 for a in applications if a.status == "shortlisted"),
                "last_7_days": sum(1 for a in applications if a.created_at >= since_7d),
            },
            "recent_activity": [
                log.to_dict()
                for log in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
            ],
        }


dashboard_service = DashboardService()
