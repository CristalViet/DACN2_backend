# 🔌 1️⃣1️⃣ app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.schemas import user as schema
from app.database import get_db
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schema.UserResponse)
def create_user(payload: schema.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.user.User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[schema.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.user.User).all()


@router.get("/{user_id}", response_model=schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schema.UserResponse)
def update_user(user_id: int, payload: schema.UserUpdate, db: Session = Depends(get_db)):
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"deleted": True}
