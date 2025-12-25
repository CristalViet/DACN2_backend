from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app import models
from app.schemas import user as schema
from app.database import get_db
from app.core.security import get_password_hash
from app.core.deps import require_admin, get_current_user
import uuid
from pathlib import Path
from typing import Optional

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
def list_users(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="Filter by role name: reader, writer, admin"),
    is_active: Optional[bool] = Query(None),
):
    """
    Get all users with filters (Admin only).
    Supports search by username/email/phone and filter by role name and active status.
    """
    query = db.query(models.user.User).options(
        selectinload(models.user.User.role)
    )
    
    # Apply search filter
    if search:
        search_filter = or_(
            models.user.User.username.ilike(f"%{search}%"),
            models.user.User.email.ilike(f"%{search}%"),
            models.user.User.phone.ilike(f"%{search}%") if models.user.User.phone else False
        )
        query = query.filter(search_filter)
    
    # Apply role filter (by role name)
    if role:
        role_obj = db.query(models.user_role.UserRole).filter(
            models.user_role.UserRole.role_name == role.lower()
        ).first()
        if role_obj:
            query = query.filter(models.user.User.role_id == role_obj.id)
        else:
            # If role doesn't exist, return empty list
            query = query.filter(False)
    
    # Apply active status filter
    if is_active is not None:
        query = query.filter(models.user.User.is_active == is_active)
    
    users = query.order_by(models.user.User.date_joined.desc()).all()
    return users


@router.get("/me", response_model=schema.UserWithRoleResponse)
def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    # Load role relationship
    user = db.query(models.user.User).options(
        selectinload(models.user.User.role)
    ).filter(models.user.User.id == current_user.id).first()
    return user


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
        
        # Handle filename - can be None for React Native uploads
        original_filename = profile_image.filename or "profile_image.jpg"
        file_ext = Path(original_filename).suffix.lower()
        
        # If no extension, try to get from content type
        if not file_ext or file_ext not in allowed_extensions:
            content_type = profile_image.content_type or ""
            if "image/jpeg" in content_type or "image/jpg" in content_type:
                file_ext = ".jpg"
            elif "image/png" in content_type:
                file_ext = ".png"
            elif "image/gif" in content_type:
                file_ext = ".gif"
            elif "image/webp" in content_type:
                file_ext = ".webp"
            else:
                file_ext = ".jpg"  # Default to jpg
        
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
            
            # Delete old image if exists (only for relative paths)
            if current_user.profile_image:
                old_image = current_user.profile_image
                # Only process if it's a relative path (starts with /static/)
                if old_image.startswith("/static/uploads/profile_images/"):
                    old_image_path = Path("static") / old_image.lstrip("/")
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


@router.get("/{user_id}", response_model=schema.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user (Public access)"""
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schema.UserResponse)
def update_user_put(
    user_id: int,
    payload: schema.UserUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user (Admin only) - PUT method"""
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=schema.UserResponse)
def update_user(
    user_id: int,
    payload: schema.UserUpdatePatch,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user (Admin only) - PATCH method.
    Supports role update by role name (string) instead of role_id.
    """
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    # Handle role conversion: if role (string) is provided, convert to role_id
    if "role" in update_data and update_data["role"]:
        role_name = update_data.pop("role")
        role_obj = db.query(models.user_role.UserRole).filter(
            models.user_role.UserRole.role_name == role_name.lower()
        ).first()
        if not role_obj:
            raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found")
        update_data["role_id"] = role_obj.id
    
    # Check for duplicate email
    if "email" in update_data and update_data["email"] != user.email:
        existing = db.query(models.user.User).filter(
            models.user.User.email == update_data["email"],
            models.user.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
    
    # Check for duplicate username
    if "username" in update_data and update_data["username"] != user.username:
        existing = db.query(models.user.User).filter(
            models.user.User.username == update_data["username"],
            models.user.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    for field, value in update_data.items():
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
