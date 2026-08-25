from app.extensions import db


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    roles = db.relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )
    