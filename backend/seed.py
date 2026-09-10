"""
Seeds an admin login plus a handful of realistic contact messages and
teacher applications, so the dashboard has something to show immediately.

Usage:
    python seed.py
"""
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import AdminUser, ContactMessage, TeacherApplication

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    import os
    seed_password = os.environ.get("ADMIN_PASSWORD")
    if not seed_password:
        raise RuntimeError("ADMIN_PASSWORD environment variable is required for seeding.")

    admin = AdminUser(email=os.environ.get("ADMIN_EMAIL", "admin@tjtutoring.academy").lower().strip(), full_name="TJ Tutoring Admin")
    admin.set_password(seed_password)
    db.session.add(admin)

    db.session.add_all([
        ContactMessage(
            name="Ngozi Adeyemi", email="ngozi.a@example.com", phone="+234 802 555 0142",
            topic="parent-enquiry",
            message="Hi, my daughter is in Grade 8 in Toronto and needs help with Mathematics. Can you support her alongside her Canadian school programme?",
            status="new", created_at=datetime.utcnow() - timedelta(hours=6),
        ),
        ContactMessage(
            name="Chidi Okonkwo", email="chidi.okonkwo@example.com", phone="+44 7700 900123",
            topic="billing",
            message="Do you accept payment in GBP directly? My son is preparing for GCSE Physics and we would like two online sessions each week.",
            status="read", created_at=datetime.utcnow() - timedelta(days=2),
        ),
        ContactMessage(
            name="Sarah Bello", email="sarah.bello@example.com", phone=None,
            topic="general",
            message="Loved the free assessment session for my son. Just wanted to say thank you "
                    "to his tutor for being so patient with him.",
            status="responded", admin_notes="Replied via WhatsApp, thanked her and asked for a testimonial.",
            created_at=datetime.utcnow() - timedelta(days=9),
        ),
    ])

    db.session.add_all([
        TeacherApplication(
            full_name="Emeka Obi", email="emeka.obi@example.com", phone="+234 803 111 2233",
            subjects="Mathematics, Physics", levels="GCSE, IGCSE, KS2 SATs",
            qualification="BSc Mechanical Engineering, University of Lagos; 3 years international curriculum tutoring",
            years_experience=3, availability="Weekday evenings across international time zones",
            location="Accra, Ghana",
            cover_note="I have taught Cambridge and Edexcel programmes for three years and also support students who need to transition between international school systems.",
            status="submitted", created_at=datetime.utcnow() - timedelta(hours=14),
        ),
        TeacherApplication(
            full_name="Grace Chukwu", email="grace.chukwu@example.com", phone="+234 805 222 3344",
            subjects="English, Basic Science", levels="KS2 SATs, Year 7-9",
            qualification="PGCE, 6 years primary teaching experience (Lagos British International School)",
            years_experience=6, availability="Mon-Thu, weekday evenings",
            location="Dublin, Ireland",
            cover_note="I currently teach primary students and would love to support international families with consistent, age-appropriate online lessons.",
            status="reviewing", admin_notes="Strong CV — schedule a demo lesson.",
            created_at=datetime.utcnow() - timedelta(days=4),
        ),
        TeacherApplication(
            full_name="Tunde Bakare", email="tunde.bakare@example.com", phone="+234 809 444 5566",
            subjects="Chemistry, Biology", levels="GCSE, IGCSE",
            qualification="MSc Biochemistry; 1 year online tutoring experience",
            years_experience=1, availability="Weekends only",
            location="Melbourne, Australia",
            status="submitted", created_at=datetime.utcnow() - timedelta(days=1),
        ),
    ])

    db.session.commit()
    print("Seeded database.")
    print("  3 contact messages, 3 teacher applications")
