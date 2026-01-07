from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, MenuItem
from app.schemas import OrderCreate, OrderResponse
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

# Create new order
@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    db_order = Order(user_id=current_user.id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    total = 0

    for item in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item {item.menu_item_id} not found"
            )

        item_total = menu_item.price * item.quantity
        total += item_total

        order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=menu_item.id,
            quantity=item.quantity,
            unit_price=menu_item.price
        )
        db.add(order_item)

    db_order.total_amount = total
    db.commit()
    db.refresh(db_order)

    return db_order


# List orders (admin sees all, staff sees own)
@router.get("/", response_model=list[OrderResponse])
def list_orders(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "admin":
        return db.query(Order).all()

    return db.query(Order).filter(Order.user_id == current_user.id).all()
