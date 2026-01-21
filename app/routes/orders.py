# app/routes/orders.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, MenuItem, User
from app.schemas import OrderCreate, OrderResponse
from app.dependencies import get_db, get_current_user, get_optional_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ======================================================
# CREATE ORDER
# - Public (guest allowed)
# - Logged-in users allowed
# ======================================================
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )

    # Create order (user_id=None for guests)
    db_order = Order(
        user_id=current_user.id if current_user else None,
        total_amount=0.0
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    total_amount = 0.0

    for item in order.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item quantity must be greater than zero"
            )

        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id,
            MenuItem.is_available == True
        ).first()

        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not available"
            )

        line_total = menu_item.price * item.quantity
        total_amount += line_total

        db_order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=menu_item.id,
            quantity=item.quantity,
            unit_price=menu_item.price
        )
        db.add(db_order_item)

    # Update order total
    db_order.total_amount = total_amount
    db.commit()
    db.refresh(db_order)

    return db_order


# ======================================================
# LIST ORDERS
# - Authentication required
# - Admin: all orders
# - User: only own orders
# ======================================================
@router.get(
    "/",
    response_model=List[OrderResponse]
)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(Order).order_by(Order.created_at.desc()).all()

    return db.query(Order).filter(Order.user_id == current_user.id).order_by(
        Order.created_at.desc()
    ).all()
