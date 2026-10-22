from app.core.errors import NotFoundApiError
from app.extensions import db
from app.models import ContactMessage, log_action
from app.services.mailer import notify_new_contact


class ContactService:
    def submit(self, data):
        message = ContactMessage(
            name=data["name"].strip(),
            email=data["email"].strip().lower(),
            phone=data.get("phone"),
            topic=data.get("topic", "general"),
            message=data["message"].strip(),
            status="new",
        )
        db.session.add(message)
        db.session.commit()
        notify_new_contact(message)
        return message

    def list(self, status=None, page=1, per_page=20):
        query = ContactMessage.query
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(ContactMessage.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get(self, message_id):
        message = ContactMessage.query.get(message_id)
        if not message:
            raise NotFoundApiError("Message not found.")
        return message

    def update(self, admin, message_id, data):
        message = self.get(message_id)
        if "status" in data:
            message.status = data["status"]
        if "admin_notes" in data:
            message.admin_notes = data["admin_notes"]
        log_action(admin.id, "contact.update", "ContactMessage", message.id)
        db.session.commit()
        return message

    def mark_read_if_new(self, message):
        if message.status == "new":
            message.status = "read"
            db.session.commit()
        return message

    def delete(self, admin, message_id):
        message = self.get(message_id)
        log_action(admin.id, "contact.delete", "ContactMessage", message.id)
        db.session.delete(message)
        db.session.commit()


contact_service = ContactService()
