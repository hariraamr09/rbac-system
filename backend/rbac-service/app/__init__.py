from flask import Flask

from .config import Config
from .extensions import db, migrate, jwt


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models
    from app import models

    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    @app.get("/")
    def home():
        return {
            "message": "RBAC API is running"
        }

    return app