import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")

    _db_url = os.environ.get("DATABASE_URL")
    if _db_url and _db_url.startswith("postgres://"):
        # Heroku-style URLs use the old "postgres://" scheme; SQLAlchemy 1.4+ wants "postgresql://"
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///" + os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dev.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ACCESS_TOKEN_TTL = timedelta(minutes=30)
    REFRESH_TOKEN_TTL = timedelta(days=14)

    _cors_raw = os.environ.get("CORS_ORIGINS", "https://tjtutoring.academy,https://www.tjtutoring.academy")
    CORS_ORIGINS = (
        [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]
        if _cors_raw.strip() != "*"
        else "*"
    )

    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.environ.get("LOG_FORMAT", "text")  # "json" in production

    # Where a real deployment would send admin alerts for new applications/messages
    NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "hello@tjtutoring.academy")
