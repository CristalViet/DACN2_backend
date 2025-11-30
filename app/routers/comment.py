from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload, aliased
from sqlalchemy import or_
from app.database import get_db
from app import models
from app.schemas import comment as schema
from app.core.deps import get_current_user

# Import models for easier reference in selectinload
from app.models.comment import Comment
from app.models.user import User
from app.models.user_role import UserRole

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=schema.CommentResponse)
def create_comment(
    payload: schema.CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment (Authenticated users only)"""
    item = models.comment.Comment(
        summary_id=payload.summary_id,
        user_id=current_user.id,
        content=payload.content,
        parent_comment_id=payload.parent_comment_id,
        access=payload.access,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.CommentResponse])
def list_comments(db: Session = Depends(get_db)):
    """Get all comments (Public access)"""
    return db.query(models.comment.Comment).all()


@router.get("/admin-related", response_model=list[schema.CommentResponse])
def get_admin_comments_by_summary(
    summary_id: int = Query(..., description="Summary ID to filter comments"),
    db: Session = Depends(get_db)
):
    """Get comments where user role is admin or parent comment user role is admin for a specific summary (Public access)"""
    # Create aliases for parent comment joins
    parent_comment = aliased(Comment)
    parent_user = aliased(User)
    parent_role = aliased(UserRole)
    comment_user = aliased(User)
    comment_role = aliased(UserRole)
    
    query = db.query(Comment).options(
        selectinload(Comment.user).selectinload(User.role),
        selectinload(Comment.parent_comment).selectinload(Comment.user).selectinload(User.role)
    ).join(
        comment_user, Comment.user_id == comment_user.id
    ).join(
        comment_role, comment_user.role_id == comment_role.id
    ).outerjoin(
        parent_comment, Comment.parent_comment_id == parent_comment.id
    ).outerjoin(
        parent_user, parent_comment.user_id == parent_user.id
    ).outerjoin(
        parent_role, parent_user.role_id == parent_role.id
    ).filter(
        Comment.summary_id == summary_id
    ).filter(
        or_(
            comment_role.role_name == "admin",
            parent_role.role_name == "admin"
        )
    )
    
    return query.all()


@router.get("/{comment_id}", response_model=schema.CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a specific comment (Public access)"""
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    return item


@router.put("/{comment_id}", response_model=schema.CommentResponse)
def update_comment(
    comment_id: int,
    payload: schema.CommentUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment (Only owner can update)"""
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user owns the comment
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (Only owner can delete)"""
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user owns the comment
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


