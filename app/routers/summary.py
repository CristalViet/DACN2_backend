from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.database import get_db
from app import models
from app.schemas import summary as schema
from app.schemas import content_section as content_section_schema
from app.core.deps import get_current_user, require_writer
from typing import Optional

# Import models for easier reference in selectinload
from app.models.summary import Summary
from app.models.book import Book
from app.models.user import User

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
        book_id=payload.book_id,
        user_id=current_user.id,
        status=payload.status,
        audio_url=payload.audio_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    # Load book and user with relations using selectinload
    db.refresh(item)
    # Eager load book and user relationships
    item = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(models.summary.Summary.id == item.id).first()
    return item


@router.get("/", response_model=list[schema.SummaryResponse])
def list_summaries(
    status_filter: Optional[str] = Query(None, description="Filter by status: editing, waiting_for_approval, approved, rejected"),
    db: Session = Depends(get_db)
):
    """Get all summaries with optional status filter (Public access)"""
    query = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    )
    
    if status_filter:
        query = query.filter(models.summary.Summary.status == status_filter)
    
    return query.all()


@router.get("/{summary_id}/content-sections", response_model=list[content_section_schema.ContentSectionResponse])
def get_summary_content_sections(summary_id: int, db: Session = Depends(get_db)):
    """Get all content sections for a specific summary, ordered by section_order (Public access)"""
    # Verify summary exists
    summary = db.get(models.summary.Summary, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # Get content sections ordered by section_order
    content_sections = db.query(models.content_section.ContentSection).filter(
        models.content_section.ContentSection.summary_id == summary_id
    ).order_by(models.content_section.ContentSection.section_order).all()
    
    return content_sections


@router.get("/{summary_id}", response_model=schema.SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """Get a specific summary (Public access)"""
    item = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(models.summary.Summary.id == summary_id).first()
    
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
    # Reload with book and user relationships
    item = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(models.summary.Summary.id == item.id).first()
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


@router.get("/search/approved", response_model=list[schema.SummaryResponse])
def search_approved_summaries(
    q: Optional[str] = Query(None, description="Search query for title or book title/author"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Search approved summaries (Public access)"""
    query = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(
        models.summary.Summary.status == "approved"
    )
    
    # Search by title or book title/author if query provided
    if q:
        search_term = f"%{q}%"
        query = query.outerjoin(Book).outerjoin(models.author.Author).filter(
            or_(
                models.summary.Summary.title.ilike(search_term),
                Book.title.ilike(search_term),
                models.author.Author.name.ilike(search_term)
            )
        )
    
    # Filter by category if provided (through book)
    if category_id:
        query = query.join(Book).filter(
            Book.category_id == category_id
        )
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    return query.all()


@router.get("/writer/me", response_model=list[schema.SummaryResponse])
def get_my_summaries(
    status_filter: Optional[str] = Query(None, description="Filter by status: editing, waiting_for_approval, approved, rejected"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summaries written by current user (Authenticated users only)"""
    query = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(
        models.summary.Summary.user_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(models.summary.Summary.status == status_filter)
    
    return query.all()


@router.get("/writer/{user_id}", response_model=list[schema.SummaryResponse])
def get_writer_summaries(
    user_id: int,
    status_filter: Optional[str] = Query(None, description="Filter by status: editing, waiting_for_approval, approved, rejected"),
    db: Session = Depends(get_db)
):
    """Get summaries written by a specific writer (Public access)"""
    query = db.query(models.summary.Summary).options(
        selectinload(Summary.book).selectinload(Book.category),
        selectinload(Summary.book).selectinload(Book.author),
        selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Summary.user)
    ).filter(
        models.summary.Summary.user_id == user_id
    )
    
    if status_filter:
        query = query.filter(models.summary.Summary.status == status_filter)
    
    return query.all()

