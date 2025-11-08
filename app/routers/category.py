from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import category as schema

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=schema.CategoryResponse)
def create_category(payload: schema.CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.category.Category).filter(models.category.Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    item = models.category.Category(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.category.Category).all()


@router.get("/{category_id}", response_model=schema.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    return item


@router.put("/{category_id}", response_model=schema.CategoryResponse)
def update_category(category_id: int, payload: schema.CategoryUpdate, db: Session = Depends(get_db)):
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        item.name = payload.name
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    item = db.get(models.category.Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


