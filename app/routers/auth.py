from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import auth as schema
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app import models

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(payload: schema.LoginRequest, db: Session = Depends(get_db)):
    # 1️⃣ Find user by email
    user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    
    # 2️⃣ Verify user and password
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 3️⃣ Create JWT token
    token = create_access_token(subject=user.id)
    
    # 4️⃣ Prepare user data to return
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "is_active": user.is_active,
        "role": user.role.role_name if user.role else None
    }
    
    # 5️⃣ Return response
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }


@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "profile_image": current_user.profile_image,
        "bio": current_user.bio,
        "is_active": current_user.is_active,
    }


