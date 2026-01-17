# app/routes/menu.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import MenuItem as MenuItemModel
from app.schemas import (
    MenuItem as MenuItemSchema,
    MenuItemCreate,
    MenuItemUpdate
)
from app.dependencies import get_db, require_role

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("/", response_model=List[MenuItemSchema])
def list_menu(db: Session = Depends(get_db)):
    return db.query(MenuItemModel).all()


@router.get("/{item_id}", response_model=MenuItemSchema)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.post(
    "/",
    response_model=MenuItemSchema,
    dependencies=[Depends(require_role("admin"))]
)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    db_item = MenuItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put(
    "/{item_id}",
    response_model=MenuItemSchema,
    dependencies=[Depends(require_role("admin"))]
)
def update_menu_item(
    item_id: int,
    item: MenuItemUpdate,
    db: Session = Depends(get_db)
):
    db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete(
    "/{item_id}",
    dependencies=[Depends(require_role("admin"))]
)
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(db_item)
    db.commit()
    return {"detail": "Menu item deleted"}
