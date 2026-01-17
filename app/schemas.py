# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ----------------------
# User / Auth Schemas
# ----------------------
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ----------------------
# Menu Schemas
# ----------------------
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = ""   # Add description
    price: float
    category: Optional[str] = "General"  # default to General
    is_available: bool = True          # default True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItem(MenuItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ORM mode

# ----------------------
# Orders Schemas
# ----------------------
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    menu_item_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
