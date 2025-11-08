from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import auth as schema
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app import models

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schema.Token)
def login(payload: schema.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=user.user_id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }


