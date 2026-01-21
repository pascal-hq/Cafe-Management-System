/* =========================
   CONFIG Wuuuuuuui
========================= */
const API_URL = "http://127.0.0.1:8000";
const CURRENCY = "KES";

/* =========================
   AUTH HELPERS
========================= */
function isLoggedIn() {
    return Boolean(localStorage.getItem("token"));
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "index.html";
}

/* =========================
   CENTRAL API HANDLER
   - ALWAYS sends JSON headers
   - Adds Authorization only if needed
========================= */
async function apiFetch(url, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
        ...(options.auth !== false && isLoggedIn()
            ? { Authorization: `Bearer ${localStorage.getItem("token")}` }
            : {})
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        if (isLoggedIn()) logout();
        throw new Error("Unauthorized");
    }

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Request failed");
    }

    return response.json();
}

/* =========================
   ADMIN LOGIN
========================= */
async function login(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("loginMessage");

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
        if (message) message.textContent = err.message;
    }
}

/* =========================
   PAGE PROTECTION
========================= */
function protectPage(requiredRole) {
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
let cart = [];

/* ---------- Load Menu ---------- */
async function loadMenu() {
    const menuDiv = document.getElementById("menuList");
    if (!menuDiv) return;

    menuItems = await apiFetch(`${API_URL}/menu/`, { auth: false });

    menuDiv.innerHTML = menuItems
        .filter(item => item.is_available)
        .map(item => `
            <div class="menu-item">
                <span>${item.name} — ${CURRENCY} ${item.price.toFixed(2)}</span>
                <button onclick="addToCart(${item.id})">Add</button>
            </div>
        `)
        .join("");
}

/* ---------- Add Item ---------- */
function addToCart(itemId) {
    const item = menuItems.find(i => i.id === itemId);
    if (!item) return;

    const existing = cart.find(i => i.menu_item_id === itemId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({
            menu_item_id: item.id,
            name: item.name,
            unit_price: item.price,
            quantity: 1
        });
    }

    renderCart();
}

/* ---------- Render Cart ---------- */
function renderCart() {
    const list = document.getElementById("orderList");
    const totalDiv = document.getElementById("orderTotal");
    if (!list || !totalDiv) return;

    let total = 0;

    list.innerHTML = cart.map(item => {
        const lineTotal = item.unit_price * item.quantity;
        total += lineTotal;

        return `
            <div class="order-item">
                <span>${item.name} × ${item.quantity}</span>
                <span>${CURRENCY} ${lineTotal.toFixed(2)}</span>
            </div>
        `;
    }).join("");

    totalDiv.textContent = `Total: ${CURRENCY} ${total.toFixed(2)}`;
}

/* ---------- Submit Order ---------- */
async function submitOrder() {
    if (cart.length === 0) {
        alert("Order is empty");
        return;
    }

    try {
        await apiFetch(`${API_URL}/orders/`, {
            method: "POST",
            auth: false, // guests allowed
            body: JSON.stringify({
                items: cart.map(item => ({
                    menu_item_id: item.menu_item_id,
                    quantity: item.quantity
                }))
            })
        });

        cart = [];
        renderCart();
        alert("Order placed successfully!");
    } catch (err) {
        alert(`Order failed: ${err.message}`);
    }
}

/* =========================
   ORDER HISTORY (LOGGED IN)
========================= */
async function loadOrders() {
    const ordersDiv = document.getElementById("ordersList");
    if (!ordersDiv) return;

    if (!isLoggedIn()) {
        ordersDiv.innerHTML = "<p>Login to see your order history.</p>";
        return;
    }

    try {
        const orders = await apiFetch(`${API_URL}/orders/`);

        ordersDiv.innerHTML = orders.map(order => `
            <div class="card">
                <h3>Order #${order.id}</h3>
                <p>${new Date(order.created_at).toLocaleString()}</p>
                <ul>
                    ${order.items.map(i =>
                        `<li>${i.quantity} × ${i.menu_item_id} @ ${CURRENCY} ${i.unit_price.toFixed(2)}</li>`
                    ).join("")}
                </ul>
                <strong>Total: ${CURRENCY} ${order.total_amount.toFixed(2)}</strong>
            </div>
        `).join("");
    } catch (err) {
        ordersDiv.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

/* =========================
   ADMIN MENU CRUD
========================= */
async function loadAdminMenu() {
    const list = document.getElementById("adminMenuList");
    const select = document.getElementById("updateSelect");
    if (!list || !select) return;

    const items = await apiFetch(`${API_URL}/menu/`);

    list.innerHTML = items.map(i => `
        <li>
            <b>${i.name}</b> — ${CURRENCY} ${i.price.toFixed(2)}
            <button onclick="deleteItem(${i.id})" class="danger">Delete</button>
        </li>
    `).join("");

    select.innerHTML =
        `<option value="">Select item</option>` +
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

async function deleteItem(id) {
    await apiFetch(`${API_URL}/menu/${id}`, { method: "DELETE" });
    loadAdminMenu();
}

/* =========================
   AUTO INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
    // Login
    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", login);

    // Customer pages
    if (document.getElementById("menuList")) {
        loadMenu();
        loadOrders();
    }

    // Admin pages
    if (document.getElementById("adminMenuList")) {
        if (!protectPage("admin")) return;

        addForm?.addEventListener("submit", addItem);
        updateForm?.addEventListener("submit", updateItem);
        logoutBtn?.addEventListener("click", logout);

        loadAdminMenu();
    }
});
//Headache beyond belief 
//Just want to sleep
//But code must keep going  
