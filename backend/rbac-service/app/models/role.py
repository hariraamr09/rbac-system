from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    users = db.relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )

    permissions = db.relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )