import logging

from flask import Flask, jsonify

from app.config import Config
from app.extensions import cors, db, limiter, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    limiter.init_app(app)

    _configure_logging(app)
    _register_error_handlers(app)

    from app.api.v1 import register_v1
    register_v1(app)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "tj-tutoring-academy-api"}

    return app


def _configure_logging(app):
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _register_error_handlers(app):
    from marshmallow import ValidationError

    from app.core.errors import ApiError

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"error": {"code": "validation_error", "message": "Invalid input.", "details": err.messages}}), 422

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"error": {"code": "not_found", "message": "Resource not found."}}), 404

    @app.errorhandler(429)
    def handle_rate_limit(err):
        return jsonify({"error": {"code": "rate_limited", "message": "Too many requests. Please try again shortly."}}), 429

    @app.errorhandler(500)
    def handle_server_error(err):
        app.logger.exception("Unhandled server error")
        return jsonify({"error": {"code": "server_error", "message": "Something went wrong. Please try again."}}), 500
