from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User


def has_permission(user, permission_name):
    """
    Check whether a user has a specific permission
    through any assigned role.
    """

    for role in user.roles:

        for permission in role.permissions:

            if permission.name == permission_name:
                return True

    return False


def require_permission(permission_name):
    """
    Protect a route using a required RBAC permission.
    """

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(user_id)

            if not user:

                return jsonify({
                    "message": "User not found"
                }), 404

            if not has_permission(user, permission_name):

                return jsonify({
                    "message": "Permission denied",
                    "required_permission": permission_name
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator