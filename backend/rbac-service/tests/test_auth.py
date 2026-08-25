def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"


def test_register_missing_body(client):
    response = client.post("/auth/register")

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Bad Request"
    assert data["message"] == "Request body is required."


def test_register_missing_username(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Username is required."


def test_register_short_username(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "hi",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Username must be at least 3 characters."


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Password must be at least 6 characters."


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "mypassword"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Enter a valid email address."


def test_duplicate_registration(client):

    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Conflict"
    assert data["message"] == "Username or email already exists."


def test_duplicate_email(client):

    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 409


def test_login(client):

    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert data["access_token"]


def test_login_wrong_password(client):

    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "mypassword"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Unauthorized"
    assert data["message"] == "Invalid email or password."


def test_login_unknown_email(client):

    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "mypassword"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Unauthorized"
    assert data["message"] == "Invalid email or password."


def test_login_missing_email(client):

    response = client.post(
        "/auth/login",
        json={
            "password": "mypassword"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Email is required."


def test_login_missing_password(client):

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "Password is required."