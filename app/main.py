# app/main.py
from fastapi import FastAPI
from .database import engine
from . import models
from .routes import users   # Auth routes
from .routes import menu    # Menu CRUD routes
from .routes import orders  # Orders routes

app = FastAPI(
    title="Cafe Management System",
    description="API for managing cafe orders, menu, and sales",
    version="1.0.0"
)

# Create tables
models.Base.metadata.create_all(bind=engine)

# Include auth routes
app.include_router(users.router)

# Include menu routes (CRUD for menu items)
app.include_router(menu.router)

# Include orders routes (CRUD for orders)
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Cafe Management System API is running"}
