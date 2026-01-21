# Cafe Management System


This repository contains a full-stack Cafe Management System built with a FastAPI backend and a vanilla JavaScript frontend. The system provides role-based access for customers and administrators, allowing for menu management, order placement, and viewing order history.

## Features
*   **RESTful API:** A robust backend built with FastAPI to manage menu items, orders, and users.
*   **Role-Based Access Control:** Distinct interfaces and permissions for `admin` and `customer` roles.
    *   **Admins:** Can perform full CRUD operations on menu items.
    *   **Customers:** Can view the menu and place orders.
*   **JWT Authentication:** Secure admin-only endpoints using JSON Web Tokens.
*   **Database Integration:** Uses SQLite with SQLAlchemy ORM for data persistence.
*   **Dynamic Frontend:** A clean, responsive user interface built with HTML, CSS, and plain JavaScript that interacts with the backend API.
*   **Guest & User Orders:** Supports order placement for both authenticated users and anonymous guests.

## Tech Stack
*   **Backend:** Python, FastAPI, SQLAlchemy, Uvicorn, Passlib, python-jose
*   **Frontend:** HTML, CSS, Vanilla JavaScript
*   **Database:** SQLite

## Project Structure
```
.
├── app/                  # FastAPI backend source code
│   ├── routes/           # API route modules (menu, orders, users)
│   ├── auth.py           # Authentication logic (JWT, hashing)
│   ├── database.py       # Database session and engine setup
│   ├── dependencies.py   # FastAPI dependency injectors
│   ├── main.py           # Main FastAPI app instance
│   ├── models.py         # SQLAlchemy ORM models
│   └── schemas.py        # Pydantic data schemas
├── frontend/             # Frontend source code
│   ├── admin.html        # Admin dashboard page
│   ├── dashboard.html    # Customer/order dashboard page
│   ├── index.html        # Login/entry page
│   ├── main.js           # All frontend logic
│   └── styles.css        # CSS styles
├── cafe.db               # SQLite database file
├── create_admin.py       # Script to create an initial admin user
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites
*   Python 3.x
*   `pip`

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/pascal-hq/cafe-management-system.git
    cd cafe-management-system
    ```

2.  **Set up the Backend:**
    *   Create and activate a virtual environment:
        ```sh
        # For macOS/Linux
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   Install the required Python packages:
        ```sh
        pip install -r requirements.txt
        ```
    *   Initialize the database and create an admin user. This script will create the `cafe.db` file and all necessary tables.
        ```sh
        python create_admin.py
        ```
        This will output the default admin credentials:
        > Username: `admin`
        > Password: `admin123`

    *   Run the FastAPI server:
        ```sh
        uvicorn app.main:app --reload
        ```
        The backend API will be running at `http://127.0.0.1:8000`.

3.  **Run the Frontend:**
    *   Open the `frontend/index.html` file directly in your web browser. No separate server is required.

## Usage

#### Customer Flow
1.  Navigate to `frontend/index.html` in your browser.
2.  Click **Continue as Customer**.
3.  You will be directed to the main dashboard where you can:
    *   View the available menu items.
    *   Add items to your order.
    *   Place the order.

#### Admin Flow
1.  Navigate to `frontend/index.html` in your browser.
2.  Click **Admin Login**.
3.  Enter the credentials:
    *   **Username:** `admin`
    *   **Password:** `admin123`
4.  Upon successful login, you will be redirected to the Admin Dashboard.
5.  On the Admin Dashboard, you can:
    *   Add new items to the menu.
    *   Update existing menu items (name, price, availability).
    *   Delete menu items.
6.  Admins can also click the **Admin Panel** link (which appears on the dashboard page when logged in as admin) to view their order history if they have placed any.
