from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import user_role as schema
from app.core.deps import require_admin

router = APIRouter(prefix="/roles", tags=["UserRoles"])


@router.post("/", response_model=schema.UserRoleResponse)
def create_role(
    payload: schema.UserRoleCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new role (Admin only)"""
    existing = db.query(models.user_role.UserRole).filter(models.user_role.UserRole.role_name == payload.role_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    item = models.user_role.UserRole(role_name=payload.role_name, permissions=payload.permissions)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.UserRoleResponse])
def list_roles(db: Session = Depends(get_db)):
    """Get all roles (Public access)"""
    return db.query(models.user_role.UserRole).all()


@router.get("/{role_id}", response_model=schema.UserRoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get a specific role (Public access)"""
    item = db.get(models.user_role.UserRole, role_id)
    if not item:
        raise HTTPException(status_code=404, detail="Role not found")
    return item


@router.put("/{role_id}", response_model=schema.UserRoleResponse)
def update_role(
    role_id: int,
    payload: schema.UserRoleUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a role (Admin only)"""
    item = db.get(models.user_role.UserRole, role_id)
    if not item:
        raise HTTPException(status_code=404, detail="Role not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a role (Admin only)"""
    item = db.get(models.user_role.UserRole, role_id)
    if not item:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


