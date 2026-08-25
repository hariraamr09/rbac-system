from app import create_app
from app.extensions import db
from app.models.role import Role


app = create_app()


with app.app_context():

    roles = [
        {
            "name": "Admin",
            "description": "Full system access"
        },
        {
            "name": "Manager",
            "description": "Can manage users"
        },
        {
            "name": "Viewer",
            "description": "Read-only access"
        }
    ]

    for role_data in roles:

        existing_role = Role.query.filter_by(
            name=role_data["name"]
        ).first()

        if existing_role:
            continue

        role = Role(
            name=role_data["name"],
            description=role_data["description"]
        )

        db.session.add(role)

    db.session.commit()

    print("Default roles created successfully.")