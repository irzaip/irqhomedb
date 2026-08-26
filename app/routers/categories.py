from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.sort_order, Category.name).all()
    return {"success": True, "data": cats}


@router.post("")
def create_category(name: str = Form(...), parent_id: int = Form(0), icon: str = Form(""), db: Session = Depends(get_db)):
    cat = Category(
        name=name,
        parent_id=parent_id if parent_id else None,
        icon=icon or None,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"success": True, "data": cat}


@router.put("/{cat_id}")
def update_category(cat_id: int, name: str = "", parent_id: int = 0, icon: str = "", db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if name:
        cat.name = name
    if parent_id:
        cat.parent_id = parent_id if parent_id else None
    if icon:
        cat.icon = icon
    db.commit()
    db.refresh(cat)
    return {"success": True, "data": cat}


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"success": True, "data": {"message": "Category deleted"}}