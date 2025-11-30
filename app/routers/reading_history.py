from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app import models
from app.schemas import reading_history as schema
from app.core.deps import get_current_user

# Import models for easier reference in selectinload
from app.models.reading_history import ReadingHistory
from app.models.summary import Summary
from app.models.book import Book
from app.models.user import User

router = APIRouter(prefix="/reading-history", tags=["ReadingHistory"])


@router.post("/", response_model=schema.ReadingHistoryResponse)
def create_reading_history(
    payload: schema.ReadingHistoryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update reading history for the current user (Authenticated users only)"""
    # Check if summary exists
    summary = db.get(models.summary.Summary, payload.summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # Check if reading history already exists for this user and summary
    existing_history = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id,
        ReadingHistory.summary_id == payload.summary_id
    ).first()
    
    if existing_history:
        # Update existing history
        for field, value in payload.model_dump(exclude_unset=True, exclude={'user_id'}).items():
            setattr(existing_history, field, value)
        db.commit()
        db.refresh(existing_history)
        
        # Load with relations
        existing_history = db.query(ReadingHistory).options(
            selectinload(ReadingHistory.user),
            selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
            selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
            selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
            selectinload(ReadingHistory.summary).selectinload(Summary.user)
        ).filter(ReadingHistory.id == existing_history.id).first()
        
        return existing_history
    
    # Create new history
    item = ReadingHistory(
        user_id=current_user.id,
        summary_id=payload.summary_id,
        last_section_id=payload.last_section_id,
        progress_percent=payload.progress_percent or 0,
        time_spent=payload.time_spent or 0,
        device_type=payload.device_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Load with relations
    item = db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(ReadingHistory.id == item.id).first()
    
    return item


@router.get("/me", response_model=list[schema.ReadingHistoryResponse])
def get_my_reading_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reading history for the current user (Authenticated users only)"""
    return db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(
        ReadingHistory.user_id == current_user.id
    ).order_by(ReadingHistory.last_read_date.desc()).all()


@router.get("/", response_model=list[schema.ReadingHistoryResponse])
def list_reading_history(db: Session = Depends(get_db)):
    """Get all reading history with user and summary populated (Admin only - consider adding admin check)"""
    return db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).all()


@router.get("/{reading_id}", response_model=schema.ReadingHistoryResponse)
def get_reading_history(
    reading_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific reading history (only if it belongs to current user)"""
    item = db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(ReadingHistory.id == reading_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    
    # Check if reading history belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this reading history"
        )
    
    return item


@router.get("/summary/{summary_id}", response_model=schema.ReadingHistoryResponse)
def get_reading_history_by_summary(
    summary_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reading history for a specific summary for the current user"""
    item = db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(
        ReadingHistory.user_id == current_user.id,
        ReadingHistory.summary_id == summary_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found for this summary")
    
    return item


@router.put("/{reading_id}", response_model=schema.ReadingHistoryResponse)
def update_reading_history(
    reading_id: int,
    payload: schema.ReadingHistoryUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading history (only if it belongs to current user)"""
    item = db.get(ReadingHistory, reading_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    
    # Check if reading history belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reading history"
        )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    
    # Load with relations
    item = db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(ReadingHistory.id == item.id).first()
    
    return item


@router.put("/summary/{summary_id}", response_model=schema.ReadingHistoryResponse)
def update_reading_history_by_summary(
    summary_id: int,
    payload: schema.ReadingHistoryUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading history by summary_id for the current user"""
    item = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id,
        ReadingHistory.summary_id == summary_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found for this summary")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    
    # Load with relations
    item = db.query(ReadingHistory).options(
        selectinload(ReadingHistory.user),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.category),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.author),
        selectinload(ReadingHistory.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(ReadingHistory.summary).selectinload(Summary.user)
    ).filter(ReadingHistory.id == item.id).first()
    
    return item


@router.delete("/{reading_id}")
def delete_reading_history(
    reading_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete reading history (only if it belongs to current user)"""
    item = db.get(ReadingHistory, reading_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    
    # Check if reading history belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reading history"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.delete("/summary/{summary_id}")
def delete_reading_history_by_summary(
    summary_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete reading history by summary_id (only if it belongs to current user)"""
    item = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id,
        ReadingHistory.summary_id == summary_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found for this summary")
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


