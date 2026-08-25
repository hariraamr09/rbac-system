from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ==========================================
# REGISTER
# ==========================================

@auth_bp.post("/register")
def register():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body is required."
        }), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Username is required."
        }), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Email is required."
        }), 400

    if not isinstance(password, str) or not password:
        return jsonify({
            "error": "Bad Request",
            "message": "Password is required."
        }), 400

    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return jsonify({
            "error": "Bad Request",
            "message": "Username must be at least 3 characters."
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Bad Request",
            "message": "Password must be at least 6 characters."
        }), 400

    if "@" not in email:
        return jsonify({
            "error": "Bad Request",
            "message": "Enter a valid email address."
        }), 400

    existing_user = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "error": "Conflict",
            "message": "Username or email already exists."
        }), 409

    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


# ==========================================
# LOGIN
# ==========================================

@auth_bp.post("/login")
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body is required."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Email is required."
        }), 400

    if not isinstance(password, str) or not password:
        return jsonify({
            "error": "Bad Request",
            "message": "Password is required."
        }), 400

    email = email.strip().lower()

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid email or password."
        }), 401

    if not user.is_active:
        return jsonify({
            "error": "Unauthorized",
            "message": "User account is inactive."
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200