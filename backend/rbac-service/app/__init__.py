from flask import Flask

from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/")
    def home():
        return {
            "message": "RBAC API is running"
        }

    return app

