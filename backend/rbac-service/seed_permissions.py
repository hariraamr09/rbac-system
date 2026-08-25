from app import create_app
from app.extensions import db
from app.models.permission import Permission


app = create_app()


with app.app_context():

    permissions = [
        {
            "name": "user:create",
            "description": "Create users"
        },
        {
            "name": "user:read",
            "description": "View users"
        },
        {
            "name": "user:update",
            "description": "Update users"
        },
        {
            "name": "user:delete",
            "description": "Delete users"
        }
    ]

    for permission_data in permissions:

        existing_permission = Permission.query.filter_by(
            name=permission_data["name"]
        ).first()

        if existing_permission:
            continue

        permission = Permission(
            name=permission_data["name"],
            description=permission_data["description"]
        )

        db.session.add(permission)

    db.session.commit()

    print("Default permissions created successfully.")