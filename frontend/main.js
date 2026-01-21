/* =========================
   CONFIG
========================= */
const API_URL = "http://127.0.0.1:8000";
const CURRENCY = "KES";

/* =========================
   HELPERS
========================= */
function isLoggedIn() {
    return !!localStorage.getItem("token");
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "index.html";
}

function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
    };
}

/* =========================
   CENTRAL API HANDLER
========================= */
async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        ...options,
        headers: {
            ...(options.headers || {}),
            ...(options.auth !== false && isLoggedIn() ? authHeaders() : {})
        }
    });

    if (res.status === 401) {
        if (isLoggedIn()) logout();
        throw new Error("Unauthorized. Please login.");
    }

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Request failed");
    }

    return res.json();
}

/* =========================
   ADMIN LOGIN
========================= */
async function login(e) {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const msg = document.getElementById("loginMessage");

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username, password })
        });

        if (!res.ok) throw new Error("Invalid credentials");

        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", "admin");
        window.location.href = "admin.html";
    } catch (err) {
        if (msg) msg.textContent = err.message;
    }
}

/* =========================
   PAGE PROTECTION
========================= */
function protectPage(requiredRole = null) {
    const role = localStorage.getItem("role");
    if (requiredRole && role !== requiredRole) {
        alert("Access denied");
        window.location.href = "index.html";
        return false;
    }
    return true;
}

/* =========================
   CUSTOMER MENU & ORDER
========================= */
let menuItems = [];
let order = [];

async function loadMenu() {
    menuItems = await apiFetch(`${API_URL}/menu/`, { auth: false });
    const menuDiv = document.getElementById("menuList");
    if (!menuDiv) return;

    menuDiv.innerHTML = menuItems
        .filter(i => i.is_available)
        .map(item => `
            <div class="menu-item">
                <span>${item.name} - ${CURRENCY} ${item.price.toFixed(2)}</span>
                <button onclick="addToOrder(${item.id})">Add</button>
            </div>
        `).join("");
}

function addToOrder(id) {
    const item = menuItems.find(i => i.id === id);
    if (!item) return;

    const existing = order.find(i => i.menu_item_id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        order.push({
            menu_item_id: id,
            name: item.name,
            unit_price: item.price,
            quantity: 1
        });
    }
    renderOrder();
}

function renderOrder() {
    const orderDiv = document.getElementById("orderList");
    const totalDiv = document.getElementById("orderTotal");
    if (!orderDiv || !totalDiv) return;

    let total = 0;
    orderDiv.innerHTML = order.map(i => {
        total += i.unit_price * i.quantity;
        return `
            <div class="order-item">
                <span>${i.name} x ${i.quantity}</span>
                <span>${CURRENCY} ${ (i.unit_price * i.quantity).toFixed(2) }</span>
            </div>
        `;
    }).join("");

    totalDiv.textContent = `Total: ${CURRENCY} ${total.toFixed(2)}`;
}

async function submitOrder() {
    if (order.length === 0) return alert("Order is empty");

    try {
        await apiFetch(`${API_URL}/orders/`, {
            method: "POST",
            auth: false, // allow guest orders
            body: JSON.stringify({
                items: order.map(i => ({
                    menu_item_id: i.menu_item_id,
                    quantity: i.quantity
                }))
            })
        });

        order = [];
        renderOrder();
        alert("Order placed successfully!");
    } catch (err) {
        alert("Failed to place order: " + err.message);
    }
}

/* =========================
   ORDER HISTORY (LOGGED-IN USERS ONLY)
========================= */
async function loadOrders() {
    const ordersList = document.getElementById("ordersList");
    if (!ordersList) return;

    try {
        if (isLoggedIn()) {
            const orders = await apiFetch(`${API_URL}/orders/`);
            ordersList.innerHTML = orders.map(o => `
                <div class="card">
                    <h3>Order #${o.id}</h3>
                    <p>${new Date(o.created_at).toLocaleString()}</p>
                    <ul>
                        ${o.items.map(i => `
                            <li>${i.quantity} × ${i.menu_item_id} @ ${CURRENCY} ${i.unit_price.toFixed(2)}</li>
                        `).join("")}
                    </ul>
                    <strong>Total: ${CURRENCY} ${o.total_amount.toFixed(2)}</strong>
                </div>
            `).join("");
        } else {
            ordersList.innerHTML = "<p>Guest users cannot see order history.</p>";
        }
    } catch (err) {
        ordersList.innerHTML = `<p>Error loading orders: ${err.message}</p>`;
    }
}

/* =========================
   ADMIN CRUD
========================= */
async function loadAdminMenu() {
    const items = await apiFetch(`${API_URL}/menu/`);
    const list = document.getElementById("adminMenuList");
    const select = document.getElementById("updateSelect");
    if (!list || !select) return;

    list.innerHTML = items.map(i => `
        <li>
            <b>${i.name}</b> - ${CURRENCY} ${i.price.toFixed(2)}
            <button class="danger" onclick="deleteItem(${i.id})">Delete</button>
        </li>
    `).join("");

    select.innerHTML = `<option value="">Select item</option>` +
        items.map(i => `<option value="${i.id}">${i.name}</option>`).join("");
}

async function addItem(e) {
    e.preventDefault();
    await apiFetch(`${API_URL}/menu/`, {
        method: "POST",
        body: JSON.stringify({
            name: addName.value,
            price: parseFloat(addPrice.value),
            category: addCategory.value,
            is_available: addAvailable.checked
        })
    });
    e.target.reset();
    loadAdminMenu();
}

async function deleteItem(id) {
    await apiFetch(`${API_URL}/menu/${id}`, { method: "DELETE" });
    loadAdminMenu();
}

async function updateItem(e) {
    e.preventDefault();
    const id = updateSelect.value;
    if (!id) return alert("Select an item");

    await apiFetch(`${API_URL}/menu/${id}`, {
        method: "PUT",
        body: JSON.stringify({
            name: updateName.value || undefined,
            price: updatePrice.value ? parseFloat(updatePrice.value) : undefined,
            category: updateCategory.value || undefined,
            is_available: updateAvailable.checked
        })
    });

    e.target.reset();
    loadAdminMenu();
}

/* =========================
   AUTO INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
    // Admin login
    if (document.getElementById("loginForm")) {
        loginForm.addEventListener("submit", login);
    }

    // Customer dashboard
    if (document.getElementById("menuList")) {
        loadMenu();
        loadOrders();
    }

    // Admin dashboard
    if (document.getElementById("adminMenuList")) {
        if (!protectPage("admin")) return;
        loadAdminMenu();
        addForm.addEventListener("submit", addItem);
        updateForm.addEventListener("submit", updateItem);
        logoutBtn.addEventListener("click", logout);
    }
});
