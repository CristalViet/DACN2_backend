from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import category as schema
from app.core.deps import require_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=schema.CategoryResponse)
def create_category(
    payload: schema.CategoryCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new category (Admin only)"""
    existing = db.query(models.category.Category).filter(models.category.Category.category_name == payload.category_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    item = models.category.Category(category_name=payload.category_name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Get all categories (Public access)"""
    return db.query(models.category.Category).all()


@router.get("/{category_id}", response_model=schema.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category (Public access)"""
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    return item


@router.put("/{category_id}", response_model=schema.CategoryResponse)
def update_category(
    category_id: int,
    payload: schema.CategoryUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a category (Admin only)"""
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.category_name is not None:
        item.category_name = payload.category_name
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a category (Admin only)"""
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


