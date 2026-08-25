from app import create_app
from app.models.user import User
from app.auth.permissions import has_permission


app = create_app()


with app.app_context():

    user = User.query.filter_by(
        username="hari"
    ).first()

    print(
        "user:create:",
        has_permission(user, "user:create")
    )

    print(
        "user:read:",
        has_permission(user, "user:read")
    )

    print(
        "user:delete:",
        has_permission(user, "user:delete")
    )

    print(
        "role:create:",
        has_permission(user, "role:create")
    )