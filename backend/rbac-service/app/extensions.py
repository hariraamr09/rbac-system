from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


@jwt.unauthorized_loader
def handle_missing_token(error):
    return {
        "error": "Unauthorized",
        "message": "Authentication is required."
    }, 401


@jwt.invalid_token_loader
def handle_invalid_token(error):
    return {
        "error": "Unauthorized",
        "message": "Invalid authentication token."
    }, 401


@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return {
        "error": "Unauthorized",
        "message": "Authentication token has expired."
    }, 401