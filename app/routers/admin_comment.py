from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import admin_comment as schema
from app.core.deps import require_admin

router = APIRouter(prefix="/admin-comments", tags=["Admin Comments"])


@router.post("/", response_model=schema.AdminCommentResponse)
def create_admin_comment(
    payload: schema.AdminCommentCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create an admin comment (Admin only)"""
    item = models.admin_comment.AdminComment(
        summary_id=payload.summary_id,
        text_content=payload.text_content,
        parent_comment_id=payload.parent_comment_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.AdminCommentResponse])
def list_admin_comments(db: Session = Depends(get_db)):
    """Get all admin comments (Public access)"""
    return db.query(models.admin_comment.AdminComment).all()


@router.get("/{admin_comment_id}", response_model=schema.AdminCommentResponse)
def get_admin_comment(admin_comment_id: int, db: Session = Depends(get_db)):
    """Get a specific admin comment (Public access)"""
    item = db.get(models.admin_comment.AdminComment, admin_comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Admin comment not found")
    return item


@router.put("/{admin_comment_id}", response_model=schema.AdminCommentResponse)
def update_admin_comment(
    admin_comment_id: int,
    payload: schema.AdminCommentUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an admin comment (Admin only)"""
    item = db.get(models.admin_comment.AdminComment, admin_comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Admin comment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{admin_comment_id}")
def delete_admin_comment(
    admin_comment_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an admin comment (Admin only)"""
    item = db.get(models.admin_comment.AdminComment, admin_comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Admin comment not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

