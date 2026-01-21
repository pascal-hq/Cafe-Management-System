# app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ===============================
# AUTH / USER SCHEMAS
# ===============================
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ===============================
# MENU SCHEMAS
# ===============================
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    category: Optional[str] = "General"
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ===============================
# ORDER SCHEMAS
# ===============================
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    menu_item_id: int
    quantity: int
    unit_price: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True
