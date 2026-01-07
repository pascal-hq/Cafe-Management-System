from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import MenuItem
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItem
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

# List all menu items
@router.get("/", response_model=List[MenuItem])
def list_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

# Get item details
@router.get("/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

# Add new item (admin only)
@router.post("/", response_model=MenuItem)
def create_menu_item(item: MenuItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_item = MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Update item (admin only)
@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(item_id: int, item: MenuItemUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

# Delete item (admin only)
@router.delete("/{item_id}")
def delete_menu_item(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Menu item deleted"}
