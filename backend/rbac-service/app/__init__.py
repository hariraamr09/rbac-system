from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    @app.get("/")
    def home():
        return {
            "message": "RBAC API is running"
        }

    return app