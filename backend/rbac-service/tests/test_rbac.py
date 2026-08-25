from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


def create_user_with_role(
    username,
    email,
    password,
    role_name,
    permissions
):
    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    role = Role(
        name=role_name,
        description=f"{role_name} role"
    )

    for permission_name in permissions:
        permission = Permission(
            name=permission_name,
            description=permission_name
        )

        role.permissions.append(permission)

    user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return user


def get_token(client, email, password):

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def test_admin_can_read_users(client):

    create_user_with_role(
        "admin",
        "admin@example.com",
        "mypassword",
        "Admin",
        [
            "user:create",
            "user:read",
            "user:update",
            "user:delete"
        ]
    )

    token = get_token(
        client,
        "admin@example.com",
        "mypassword"
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_admin_can_create_user(client):

    create_user_with_role(
        "admin",
        "admin@example.com",
        "mypassword",
        "Admin",
        [
            "user:create",
            "user:read",
            "user:update",
            "user:delete"
        ]
    )

    token = get_token(
        client,
        "admin@example.com",
        "mypassword"
    )

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 201


def test_viewer_can_read_users(client):

    create_user_with_role(
        "viewer",
        "viewer@example.com",
        "mypassword",
        "Viewer",
        [
            "user:read"
        ]
    )

    token = get_token(
        client,
        "viewer@example.com",
        "mypassword"
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_viewer_cannot_create_user(client):

    create_user_with_role(
        "viewer",
        "viewer@example.com",
        "mypassword",
        "Viewer",
        [
            "user:read"
        ]
    )

    token = get_token(
        client,
        "viewer@example.com",
        "mypassword"
    )

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "username": "blocked",
            "email": "blocked@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_update_user(client):

    create_user_with_role(
        "viewer",
        "viewer@example.com",
        "mypassword",
        "Viewer",
        [
            "user:read"
        ]
    )

    target = User(
        username="target",
        email="target@example.com"
    )

    target.set_password("mypassword")

    db.session.add(target)
    db.session.commit()

    token = get_token(
        client,
        "viewer@example.com",
        "mypassword"
    )

    response = client.put(
        f"/users/{target.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "username": "changed"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_delete_user(client):

    create_user_with_role(
        "viewer",
        "viewer@example.com",
        "mypassword",
        "Viewer",
        [
            "user:read"
        ]
    )

    target = User(
        username="targetdelete",
        email="targetdelete@example.com"
    )

    target.set_password("mypassword")

    db.session.add(target)
    db.session.commit()

    token = get_token(
        client,
        "viewer@example.com",
        "mypassword"
    )

    response = client.delete(
        f"/users/{target.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
