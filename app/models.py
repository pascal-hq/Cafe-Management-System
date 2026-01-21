# app/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

# ======================
# USERS TABLE
# ======================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin / staff
    created_at = Column(DateTime, default=datetime.utcnow)

    # One user → many orders
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete"
    )


# ======================
# MENU ITEMS TABLE
# ======================
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)
    category = Column(String, default="General")
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One menu item → many order items
    order_items = relationship(
        "OrderItem",
        back_populates="menu_item"
    )


# ======================
# ORDERS TABLE
# ======================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # Nullable → allows guest orders
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    total_amount = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending / paid
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship(
        "User",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# ======================
# ORDER ITEMS TABLE
# ======================
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relationships
    order = relationship(
        "Order",
        back_populates="items"
    )

    menu_item = relationship(
        "MenuItem",
        back_populates="order_items"
    )
