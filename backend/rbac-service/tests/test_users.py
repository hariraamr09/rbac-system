import pytest

from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


@pytest.fixture
def admin_token(client):
    user = User(
        username="admin",
        email="admin@example.com"
    )

    user.set_password("mypassword")

    admin_role = Role(
        name="Admin",
        description="Full system access"
    )

    permissions = [
        Permission(
            name="user:create",
            description="Create users"
        ),
        Permission(
            name="user:read",
            description="Read users"
        ),
        Permission(
            name="user:update",
            description="Update users"
        ),
        Permission(
            name="user:delete",
            description="Delete users"
        ),
    ]

    admin_role.permissions.extend(permissions)

    user.roles.append(admin_role)

    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


@pytest.fixture
def viewer_token(client):
    user = User(
        username="viewer",
        email="viewer@example.com"
    )

    user.set_password("mypassword")

    viewer_role = Role(
        name="Viewer",
        description="Read-only access"
    )

    read_permission = Permission(
    name="user:read",
    description="Read users"
    )

    viewer_role.permissions.append(read_permission)

    user.roles.append(viewer_role)

    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "viewer@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def test_users_me_requires_authentication(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_users_me(client, admin_token):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["username"] == "admin"
    assert data["email"] == "admin@example.com"
    assert "Admin" in data["roles"]


def test_get_users_requires_permission(client, admin_token):
    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "users" in data


def test_create_user(client, admin_token):
    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == "newuser"


def test_create_user_duplicate(client, admin_token):
    client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "mypassword"
        }
    )

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "newuser",
            "email": "another@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 409


def test_update_user(client, admin_token):
    create_response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "oldname",
            "email": "old@example.com",
            "password": "mypassword"
        }
    )

    user_id = create_response.get_json()["user"]["id"]

    response = client.put(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "newname"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["user"]["username"] == "newname"


def test_update_nonexistent_user(client, admin_token):
    response = client.put(
        "/users/99999",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "newname"
        }
    )

    assert response.status_code == 404


def test_delete_user(client, admin_token):
    create_response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "mypassword"
        }
    )

    user_id = create_response.get_json()["user"]["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "User deleted successfully"


def test_viewer_cannot_create_user(client, viewer_token):
    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "username": "blocked",
            "email": "blocked@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_update_user(client, viewer_token):
    admin = User(
        username="target",
        email="target@example.com"
    )

    admin.set_password("mypassword")

    db.session.add(admin)
    db.session.commit()

    response = client.put(
        f"/users/{admin.id}",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "username": "blocked"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_delete_user(client, viewer_token):
    target = User(
        username="targetdelete",
        email="targetdelete@example.com"
    )

    target.set_password("mypassword")

    db.session.add(target)
    db.session.commit()

    response = client.delete(
        f"/users/{target.id}",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        }
    )

    assert response.status_code == 403