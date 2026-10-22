"""Staff notification emails.

New free-assessment requests / enquiries and tutor applications are emailed to
NOTIFY_EMAIL (hello@tjtutoring.academy by default) over plain SMTP. The email is
sent from a background thread so a slow mail server never delays the form
response, and a mail failure is logged but never breaks the submission: the
record is always saved to the database first and stays visible in the admin
dashboard either way.
"""
import logging
import smtplib
import ssl
import threading
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)

TOPIC_LABELS = {
    "parent-enquiry": "Free assessment request",
    "billing": "Billing / payments",
    "technical": "Technical issue",
    "partnership": "School / partnership enquiry",
    "general": "General question",
}

_CONFIG_KEYS = (
    "NOTIFY_EMAIL", "MAIL_FROM", "SMTP_HOST", "SMTP_PORT",
    "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_USE_TLS", "SMTP_USE_SSL",
)


def _one_line(value, limit=150):
    """Header values must be a single line; collapse any newlines/tabs."""
    return " ".join(str(value or "").split())[:limit]


def _deliver(cfg, subject, body, reply_to):
    try:
        msg = EmailMessage()
        msg["Subject"] = _one_line(subject)
        msg["From"] = cfg["MAIL_FROM"]
        msg["To"] = cfg["NOTIFY_EMAIL"]
        if reply_to:
            msg["Reply-To"] = _one_line(reply_to, 255)
        msg.set_content(body)

        host, port = cfg["SMTP_HOST"], int(cfg["SMTP_PORT"])
        if cfg["SMTP_USE_SSL"]:
            server = smtplib.SMTP_SSL(host, port, timeout=15, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(host, port, timeout=15)
        with server:
            if cfg["SMTP_USE_TLS"] and not cfg["SMTP_USE_SSL"]:
                server.starttls(context=ssl.create_default_context())
            if cfg["SMTP_USERNAME"]:
                server.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"] or "")
            server.send_message(msg)
        log.info("Notification email sent to %s: %s", cfg["NOTIFY_EMAIL"], msg["Subject"])
    except Exception:
        log.exception("Could not send notification email to %s", cfg.get("NOTIFY_EMAIL"))


def send_staff_email(subject, body, reply_to=None):
    """Queue an email to NOTIFY_EMAIL. Never raises. Returns True if it was queued."""
    try:
        cfg = {key: current_app.config.get(key) for key in _CONFIG_KEYS}
        if not cfg["SMTP_HOST"]:
            log.warning(
                "SMTP_HOST is not set, so no notification email was sent to %s (%s). "
                "Set SMTP_* in backend/.env to enable email notifications.",
                cfg["NOTIFY_EMAIL"], _one_line(subject),
            )
            return False
        threading.Thread(target=_deliver, args=(cfg, subject, body, reply_to), daemon=True).start()
        return True
    except Exception:
        log.exception("Could not queue notification email")
        return False


def _stamp(record):
    return record.created_at.strftime("%Y-%m-%d %H:%M UTC") if getattr(record, "created_at", None) else "just now"


def notify_new_contact(message):
    label = TOPIC_LABELS.get(message.topic, "Enquiry")
    subject = f"[TJ Tutoring] New {label.lower()} from {_one_line(message.name, 80)}"
    body = (
        f"{label} received through the website.\n\n"
        f"Name:   {message.name}\n"
        f"Email:  {message.email}\n"
        f"Phone:  {message.phone or '-'}\n"
        f"Topic:  {label}\n"
        f"Received: {_stamp(message)}\n\n"
        f"Message:\n{message.message}\n\n"
        "Reply to this email to respond to the family directly.\n"
        "It is also saved in the admin dashboard.\n"
    )
    return send_staff_email(subject, body, reply_to=message.email)


def notify_new_application(application):
    subject = f"[TJ Tutoring] New tutor application from {_one_line(application.full_name, 80)}"
    body = (
        "New tutor application received through the website.\n\n"
        f"Name:           {application.full_name}\n"
        f"Email:          {application.email}\n"
        f"Phone:          {application.phone}\n"
        f"Location:       {application.location or '-'}\n"
        f"Subjects:       {application.subjects}\n"
        f"Levels:         {application.levels or '-'}\n"
        f"Qualifications: {application.qualification}\n"
        f"Experience:     {application.years_experience} years\n"
        f"Availability:   {application.availability or '-'}\n"
        f"CV / portfolio: {application.resume_url or '-'}\n"
        f"Received:       {_stamp(application)}\n\n"
        f"Note:\n{application.cover_note or '-'}\n\n"
        "Reply to this email to respond to the applicant directly.\n"
        "It is also saved in the admin dashboard.\n"
    )
    return send_staff_email(subject, body, reply_to=application.email)
