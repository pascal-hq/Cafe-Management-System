# app/routes/menu.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import MenuItem
from app.schemas import MenuItemResponse, MenuItemCreate, MenuItemUpdate
from app.dependencies import get_db, require_role

router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)


# ======================================================
# LIST MENU ITEMS (PUBLIC)
# ======================================================
@router.get(
    "/",
    response_model=List[MenuItemResponse]
)
def list_menu_items(db: Session = Depends(get_db)):
    return (
        db.query(MenuItem)
        .order_by(MenuItem.created_at.desc())
        .all()
    )


# ======================================================
# GET SINGLE MENU ITEM (PUBLIC)
# ======================================================
@router.get(
    "/{item_id}",
    response_model=MenuItemResponse
)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item


# ======================================================
# CREATE MENU ITEM (ADMIN ONLY)
# ======================================================
@router.post(
    "/",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    existing_item = db.query(MenuItem).filter(MenuItem.name == item.name).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menu item with this name already exists"
        )
    db_item = MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ======================================================
# UPDATE MENU ITEM (ADMIN ONLY)
# ======================================================
@router.put(
    "/{item_id}",
    response_model=MenuItemResponse,
    dependencies=[Depends(require_role("admin"))]
)
def update_menu_item(item_id: int, item: MenuItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


# ======================================================
# DELETE MENU ITEM (ADMIN ONLY)
# ======================================================
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("admin"))]
)
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    db.delete(db_item)
    db.commit()
    return {"detail": "Menu item deleted successfully"}
