const API_URL = "http://127.0.0.1:5000";

let currentUser = null;


// ==============================
// DOM ELEMENTS
// ==============================

const loginSection =
    document.getElementById("loginSection");

const dashboardSection =
    document.getElementById("dashboardSection");

const loginForm =
    document.getElementById("loginForm");

const loginMessage =
    document.getElementById("loginMessage");

const logoutBtn =
    document.getElementById("logoutBtn");

const loadUsersBtn =
    document.getElementById("loadUsersBtn");

const createUserBtn =
    document.getElementById("createUserBtn");

const usersList =
    document.getElementById("usersList");

const usersMessage =
    document.getElementById("usersMessage");


// ==============================
// LOGIN
// ==============================

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    loginMessage.textContent = "";

    try {

        const response = await fetch(
            `${API_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            loginMessage.textContent =
                data.message || "Login failed.";

            return;
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        loginForm.reset();

        showDashboard();

        await loadCurrentUser();

        await loadUsers();

    } catch (error) {

        console.error("Login error:", error);

        loginMessage.textContent =
            "Cannot connect to the backend.";
    }
});


// ==============================
// LOAD CURRENT USER
// ==============================

async function loadCurrentUser() {

    const token =
        localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/users/me`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const user = await response.json();

        if (!response.ok) {

            console.error(
                "Failed to load current user:",
                user
            );

            logout();

            return;
        }

        currentUser = user;

        document.getElementById("username").textContent =
            user.username || "-";

        document.getElementById("userEmail").textContent =
            user.email || "-";

        document.getElementById("role").textContent =
            (user.roles || []).join(", ") || "No role";

        loadPermissions(
            user.permissions || []
        );

        updatePermissionControls();

    } catch (error) {

        console.error(
            "Current user error:",
            error
        );
    }
}


// ==============================
// DISPLAY PERMISSIONS
// ==============================

function loadPermissions(permissions) {

    const permissionsElement =
        document.getElementById("permissions");

    permissionsElement.innerHTML = "";

    if (!permissions || permissions.length === 0) {

        const li =
            document.createElement("li");

        li.textContent =
            "No permissions assigned.";

        permissionsElement.appendChild(li);

        return;
    }

    permissions.forEach((permission) => {

        const li =
            document.createElement("li");

        li.textContent = permission;

        permissionsElement.appendChild(li);
    });
}


// ==============================
// CHECK PERMISSION
// ==============================

function hasPermission(permission) {

    if (!currentUser) {
        return false;
    }

    if (!Array.isArray(currentUser.permissions)) {
        return false;
    }

    return currentUser.permissions.includes(
        permission
    );
}


// ==============================
// UPDATE UI BASED ON PERMISSIONS
// ==============================

function updatePermissionControls() {

    if (!createUserBtn) {
        return;
    }

    createUserBtn.classList.toggle(
        "hidden",
        !hasPermission("user:create")
    );

    renderUserActionButtons();
}


// ==============================
// LOAD USERS
// ==============================

async function loadUsers() {

    const token =
        localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    usersMessage.textContent = "";

    usersList.innerHTML = "";

    try {

        const response = await fetch(
            `${API_URL}/users/`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            usersMessage.textContent =
                data.message ||
                "Unable to load users.";

            return;
        }

        const users =
            data.users || [];

        if (users.length === 0) {

            usersList.textContent =
                "No users found.";

            return;
        }

        users.forEach((user) => {

            const userDiv =
                document.createElement("div");

            userDiv.className = "user";

            const username =
                document.createElement("strong");

            username.textContent =
                user.username;

            const email =
                document.createElement("p");

            email.textContent =
                user.email;

            const role =
                document.createElement("p");

            role.textContent =
                `Role: ${
                    (user.roles || []).join(", ") ||
                    "No role"
                }`;

            const actions =
                document.createElement("div");

            actions.className =
                "user-actions";

            userDiv.appendChild(username);
            userDiv.appendChild(email);
            userDiv.appendChild(role);
            userDiv.appendChild(actions);

            usersList.appendChild(userDiv);
        });

        renderUserActionButtons();

    } catch (error) {

        console.error(
            "Load users error:",
            error
        );

        usersMessage.textContent =
            "Cannot connect to the backend.";
    }
}


// ==============================
// RENDER EDIT / DELETE BUTTONS
// ==============================

function renderUserActionButtons() {

    const userElements =
        document.querySelectorAll(".user");

    userElements.forEach((userElement) => {

        const actions =
            userElement.querySelector(
                ".user-actions"
            );

        if (!actions) {
            return;
        }

        actions.innerHTML = "";

        const username =
            userElement.querySelector(
                "strong"
            );

        if (!username) {
            return;
        }

        const user = findUserByUsername(
            username.textContent
        );

        if (!user) {
            return;
        }


        // EDIT BUTTON

        if (hasPermission("user:update")) {

            const editButton =
                document.createElement("button");

            editButton.textContent =
                "Edit";

            editButton.addEventListener(
                "click",
                () => editUser(user.id)
            );

            actions.appendChild(
                editButton
            );
        }


        // DELETE BUTTON

        if (hasPermission("user:delete")) {

            const deleteButton =
                document.createElement("button");

            deleteButton.textContent =
                "Delete";

            deleteButton.classList.add(
                "danger"
            );

            deleteButton.addEventListener(
                "click",
                () => deleteUser(user.id)
            );

            actions.appendChild(
                deleteButton
            );
        }
    });
}


// ==============================
// FIND USER
// ==============================

async function getUsersFromAPI() {

    const token =
        localStorage.getItem("access_token");

    if (!token) {
        return [];
    }

    try {

        const response =
            await fetch(
                `${API_URL}/users/`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            return [];
        }

        return data.users || [];

    } catch (error) {

        console.error(
            "Get users error:",
            error
        );

        return [];
    }
}


function findUserByUsername(username) {

    const userElements =
        document.querySelectorAll(".user");

    for (const element of userElements) {

        const strong =
            element.querySelector("strong");

        if (
            strong &&
            strong.textContent === username
        ) {
            return {
                id: element.dataset.userId
            };
        }
    }

    return null;
}


// ==============================
// DELETE USER
// ==============================

async function deleteUser(userId) {

    if (!hasPermission("user:delete")) {

        alert(
            "You do not have permission to delete users."
        );

        return;
    }

    const confirmed =
        confirm(
            "Are you sure you want to delete this user?"
        );

    if (!confirmed) {
        return;
    }

    const token =
        localStorage.getItem("access_token");

    try {

        const response =
            await fetch(
                `${API_URL}/users/${userId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.message ||
                "Unable to delete user."
            );

            return;
        }

        await loadUsers();

    } catch (error) {

        console.error(
            "Delete user error:",
            error
        );

        alert(
            "Cannot connect to the backend."
        );
    }
}


// ==============================
// EDIT USER
// ==============================

async function editUser(userId) {

    if (!hasPermission("user:update")) {

        alert(
            "You do not have permission to update users."
        );

        return;
    }

    const newUsername =
        prompt(
            "Enter the new username:"
        );

    if (!newUsername) {
        return;
    }

    const token =
        localStorage.getItem("access_token");

    try {

        const response =
            await fetch(
                `${API_URL}/users/${userId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        username:
                            newUsername.trim()
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.message ||
                "Unable to update user."
            );

            return;
        }

        await loadUsers();

    } catch (error) {

        console.error(
            "Edit user error:",
            error
        );

        alert(
            "Cannot connect to the backend."
        );
    }
}


// ==============================
// CREATE USER
// ==============================

async function createUser() {

    if (!hasPermission("user:create")) {

        alert(
            "You do not have permission to create users."
        );

        return;
    }

    const username =
        prompt("Username:");

    if (!username) {
        return;
    }

    const email =
        prompt("Email:");

    if (!email) {
        return;
    }

    const password =
        prompt("Password:");

    if (!password) {
        return;
    }

    const token =
        localStorage.getItem("access_token");

    try {

        const response =
            await fetch(
                `${API_URL}/users/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        username:
                            username.trim(),

                        email:
                            email.trim(),

                        password
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.message ||
                "Unable to create user."
            );

            return;
        }

        await loadUsers();

    } catch (error) {

        console.error(
            "Create user error:",
            error
        );

        alert(
            "Cannot connect to the backend."
        );
    }
}


// ==============================
// LOGOUT
// ==============================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    currentUser = null;

    dashboardSection.classList.add(
        "hidden"
    );

    loginSection.classList.remove(
        "hidden"
    );

    logoutBtn.classList.add(
        "hidden"
    );

    loginMessage.textContent = "";

    usersMessage.textContent = "";

    usersList.innerHTML = "";

    loginForm.reset();

    if (createUserBtn) {
        createUserBtn.classList.add(
            "hidden"
        );
    }
}


// ==============================
// SHOW DASHBOARD
// ==============================

function showDashboard() {

    loginSection.classList.add(
        "hidden"
    );

    dashboardSection.classList.remove(
        "hidden"
    );

    logoutBtn.classList.remove(
        "hidden"
    );
}


// ==============================
// HTML ESCAPING
// ==============================

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


// ==============================
// EVENT LISTENERS
// ==============================

logoutBtn.addEventListener(
    "click",
    logout
);


loadUsersBtn.addEventListener(
    "click",
    loadUsers
);


if (createUserBtn) {

    createUserBtn.addEventListener(
        "click",
        createUser
    );
}


// ==============================
// CHECK EXISTING SESSION
// ==============================

const existingToken =
    localStorage.getItem(
        "access_token"
    );

if (existingToken) {

    showDashboard();

    loadCurrentUser()
        .then(() => loadUsers());
}