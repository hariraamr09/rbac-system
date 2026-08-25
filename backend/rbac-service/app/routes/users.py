from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.auth.permissions import require_permission


users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@users_bp.get("/me")
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id)
    )

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "User not found."
        }), 404

    permissions = sorted({
        permission.name
        for role in user.roles
        for permission in role.permissions
    })

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [
            role.name
            for role in user.roles
        ],
        "permissions": permissions
    }), 200


@users_bp.get("/")
@require_permission("user:read")
def get_users():

    users = User.query.order_by(
        User.id
    ).all()

    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": [
                    role.name
                    for role in user.roles
                ]
            }
            for user in users
        ]
    }), 200


@users_bp.get("/<int:user_id>")
@require_permission("user:read")
def get_user(user_id):

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "User not found."
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [
            role.name
            for role in user.roles
        ]
    }), 200


@users_bp.post("/")
@require_permission("user:create")
def create_user():

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
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


@users_bp.put("/<int:user_id>")
@require_permission("user:update")
def update_user(user_id):

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "User not found."
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body is required."
        }), 400

    if (
        "username" not in data
        and "email" not in data
        and "password" not in data
    ):
        return jsonify({
            "error": "Bad Request",
            "message": "At least one field is required."
        }), 400

    if "username" in data:

        username = data["username"]

        if not isinstance(username, str) or not username.strip():
            return jsonify({
                "error": "Bad Request",
                "message": "Username cannot be empty."
            }), 400

        username = username.strip()

        if len(username) < 3:
            return jsonify({
                "error": "Bad Request",
                "message": "Username must be at least 3 characters."
            }), 400

        existing_user = User.query.filter(
            User.username == username,
            User.id != user_id
        ).first()

        if existing_user:
            return jsonify({
                "error": "Conflict",
                "message": "Username already exists."
            }), 409

        user.username = username

    if "email" in data:

        email = data["email"]

        if not isinstance(email, str) or not email.strip():
            return jsonify({
                "error": "Bad Request",
                "message": "Email cannot be empty."
            }), 400

        email = email.strip().lower()

        if "@" not in email:
            return jsonify({
                "error": "Bad Request",
                "message": "Enter a valid email address."
            }), 400

        existing_user = User.query.filter(
            User.email == email,
            User.id != user_id
        ).first()

        if existing_user:
            return jsonify({
                "error": "Conflict",
                "message": "Email already exists."
            }), 409

        user.email = email

    if "password" in data:

        password = data["password"]

        if not isinstance(password, str) or not password:
            return jsonify({
                "error": "Bad Request",
                "message": "Password cannot be empty."
            }), 400

        if len(password) < 6:
            return jsonify({
                "error": "Bad Request",
                "message": "Password must be at least 6 characters."
            }), 400

        user.set_password(password)

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


@users_bp.delete("/<int:user_id>")
@require_permission("user:delete")
def delete_user(user_id):

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "User not found."
        }), 404

    current_user_id = int(
        get_jwt_identity()
    )

    if user.id == current_user_id:
        return jsonify({
            "error": "Bad Request",
            "message": "You cannot delete your own account."
        }), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200


@users_bp.post("/<int:user_id>/roles")
@jwt_required()
def assign_role(user_id):

    data = request.get_json(silent=True)

    if not data or not data.get("role_id"):
        return jsonify({
            "error": "Bad Request",
            "message": "role_id is required."
        }), 400

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "Not Found",
            "message": "User not found."
        }), 404

    role = db.session.get(
        Role,
        data["role_id"]
    )

    if not role:
        return jsonify({
            "error": "Not Found",
            "message": "Role not found."
        }), 404

    if role in user.roles:
        return jsonify({
            "error": "Conflict",
            "message": "Role already assigned."
        }), 409

    user.roles.append(role)

    db.session.commit()

    return jsonify({
        "message": "Role assigned successfully",
        "user_id": user.id,
        "role": role.name
    }), 200