from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, jwt
from .errors import register_error_handlers


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(app)

    register_error_handlers(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    @app.get("/")
    def home():
        return {
            "message": "RBAC API is running"
        }

    return app