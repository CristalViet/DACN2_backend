from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import comment as schema
from app.core.deps import get_current_user

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


