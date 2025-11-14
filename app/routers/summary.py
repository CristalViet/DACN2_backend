from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import summary as schema
from app.core.deps import get_current_user, require_writer

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/", response_model=schema.SummaryResponse)
def create_summary(
    payload: schema.SummaryCreate,
    current_user = Depends(require_writer),
    db: Session = Depends(get_db)
):
    """Create a new summary (Writer or Admin only)"""
    item = models.summary.Summary(
        title=payload.title,
        book_author=payload.book_author,
        book_cover_path=payload.book_cover_path,
        published_date=payload.published_date,
        category_id=payload.category_id,
        user_id=current_user.id,
        status=payload.status,
        audio_url=payload.audio_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.SummaryResponse])
def list_summaries(db: Session = Depends(get_db)):
    """Get all summaries (Public access)"""
    return db.query(models.summary.Summary).all()


@router.get("/{summary_id}", response_model=schema.SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """Get a specific summary (Public access)"""
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    return item


@router.put("/{summary_id}", response_model=schema.SummaryResponse)
def update_summary(
    summary_id: int,
    payload: schema.SummaryUpdate,
    current_user = Depends(require_writer),
    db: Session = Depends(get_db)
):
    """Update a summary (Writer or Admin only)"""
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # Check if user owns the summary or is admin
    if item.user_id != current_user.id and current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this summary"
        )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{summary_id}")
def delete_summary(
    summary_id: int,
    current_user = Depends(require_writer),
    db: Session = Depends(get_db)
):
    """Delete a summary (Writer or Admin only)"""
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # Check if user owns the summary or is admin
    if item.user_id != current_user.id and current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this summary"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


