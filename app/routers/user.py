from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models
from app.schemas import user as schema
from app.database import get_db
from app.core.security import get_password_hash
from app.core.deps import require_admin, get_current_user
import uuid
from pathlib import Path

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schema.UserResponse)
def create_user(
    payload: schema.UserCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)"""
    existing = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.user.User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[schema.UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Get all users (Public access)"""
    return db.query(models.user.User).all()


@router.get("/{user_id}", response_model=schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user (Public access)"""
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schema.UserResponse)
def update_user(
    user_id: int,
    payload: schema.UserUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user (Admin only)"""
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (Admin only)"""
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"deleted": True}


@router.patch("/me", response_model=schema.UserResponse)
async def update_current_user(
    username: str | None = Form(None),
    email: str | None = Form(None),
    phone: str | None = Form(None),
    bio: str | None = Form(None),
    profile_image: UploadFile | None = File(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's information with optional image upload"""
    # Create uploads directory if it doesn't exist
    upload_dir = Path("static/uploads/profile_images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle image upload
    if profile_image:
        # Validate file type
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_ext = Path(profile_image.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = upload_dir / filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await profile_image.read()
                buffer.write(content)
            
            # Store relative path in database
            image_url = f"/static/uploads/profile_images/{filename}"
            
            # Delete old image if exists
            if current_user.profile_image:
                old_image_path = Path("static") / current_user.profile_image.lstrip("/")
                if old_image_path.exists():
                    old_image_path.unlink()
            
            current_user.profile_image = image_url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save image: {str(e)}"
            )
    
    # Update other fields
    if username is not None:
        # Check if username is already taken by another user
        existing_user = db.query(models.user.User).filter(
            models.user.User.username == username,
            models.user.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = username
    
    if email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(models.user.User).filter(
            models.user.User.email == email,
            models.user.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = email
    
    if phone is not None:
        current_user.phone = phone
    
    if bio is not None:
        current_user.bio = bio
    
    db.commit()
    db.refresh(current_user)
    return current_user
