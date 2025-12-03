from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.schemas import auth as schema
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.deps import get_current_user
from app import models
from app.helpers.email import send_otp_email
from app.helpers.otp_storage import otp_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: schema.RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    Returns user data in EndUser format (same as /auth/me).
    """
    logger.info(f"Register attempt for email: {payload.email}, username: {payload.username}")
    
    # 1️⃣ Check if email already exists
    existing_user = db.query(models.user.User).filter(
        models.user.User.email == payload.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2️⃣ Check if username already exists
    existing_username = db.query(models.user.User).filter(
        models.user.User.username == payload.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 3️⃣ Get default "reader" role
    reader_role = db.query(models.user_role.UserRole).filter(
        models.user_role.UserRole.role_name == "reader"
    ).first()
    
    if not reader_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not found. Please contact administrator."
        )
    
    # 4️⃣ Create new user
    new_user = models.user.User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        phone=payload.phone,
        role_id=reader_role.id,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5️⃣ Return user data in EndUser format (same as /auth/me)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "phone": new_user.phone,
        "is_active": new_user.is_active,
        "role": reader_role.role_name
    }


@router.post("/login/request-otp")
def request_otp(payload: schema.RequestOTPRequest, db: Session = Depends(get_db)):
    """
    Request OTP for login.
    If password is provided, verifies email and password.
    If password is not provided, only checks if email exists.
    """
    # 1️⃣ Find user by email
    user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # 2️⃣ Verify password if provided
    if payload.password:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
    
    # 3️⃣ Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # 4️⃣ Generate and store OTP
    otp_code = otp_storage.store_otp(payload.email, user.id)
    
    # 5️⃣ Send OTP via email
    email_sent = send_otp_email(payload.email, otp_code)
    
    if not email_sent:
        logger.error(f"Failed to send OTP email to {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again later."
        )
    
    logger.info(f"OTP requested for {payload.email}")
    
    # 6️⃣ Return success response
    return {
        "message": "OTP sent successfully",
        "email": payload.email  # Return email for frontend confirmation
    }


@router.post("/login/verify-otp")
def verify_otp(payload: schema.VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify OTP code and return access token.
    """
    # 1️⃣ Verify OTP
    user_id = otp_storage.verify_otp(payload.email, payload.otp)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP code"
        )
    
    # 2️⃣ Get user from database
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 3️⃣ Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # 4️⃣ Create JWT token
    token = create_access_token(subject=user.id)
    
    # 5️⃣ Prepare user data to return
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "is_active": user.is_active,
        "role": user.role.role_name if user.role else None
    }
    
    logger.info(f"OTP verified successfully for {payload.email}")
    
    # 6️⃣ Return response (same format as login)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }


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
    from app.helpers.url import get_full_image_url
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "profile_image": get_full_image_url(current_user.profile_image),
        "bio": current_user.bio,
        "is_active": current_user.is_active,
        "role": current_user.role.role_name
    }


