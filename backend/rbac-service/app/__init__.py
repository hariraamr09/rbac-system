from flask import Flask

from .config import Config
from .extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return {
            "message": "RBAC API is running"
        }

    return app

#hiii