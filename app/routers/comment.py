from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import comment as schema

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=schema.CommentResponse)
def create_comment(payload: schema.CommentCreate, db: Session = Depends(get_db)):
    item = models.comment.Comment(
        user_id=payload.user_id,
        summary_id=payload.summary_id,
        content=payload.content,
        parent_comment_id=payload.parent_comment_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.CommentResponse])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.comment.Comment).all()


@router.get("/{comment_id}", response_model=schema.CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    return item


@router.put("/{comment_id}", response_model=schema.CommentResponse)
def update_comment(comment_id: int, payload: schema.CommentUpdate, db: Session = Depends(get_db)):
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    item = db.get(models.comment.Comment, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


