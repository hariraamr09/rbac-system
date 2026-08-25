from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.role import Role


users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@users_bp.get("/me")
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [
            role.name for role in user.roles
        ]
    }), 200


@users_bp.post("/<int:user_id>/roles")
@jwt_required()
def assign_role(user_id):

    data = request.get_json()

    if not data or not data.get("role_id"):
        return jsonify({
            "message": "role_id is required"
        }), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    role = Role.query.get(data["role_id"])

    if not role:
        return jsonify({
            "message": "Role not found"
        }), 404

    if role in user.roles:
        return jsonify({
            "message": "Role already assigned"
        }), 409

    user.roles.append(role)

    db.session.commit()

    return jsonify({
        "message": "Role assigned successfully",
        "user_id": user.id,
        "role": role.name
    }), 200