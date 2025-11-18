from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import models
from app.schemas import summary as schema
from app.core.deps import get_current_user

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/", response_model=schema.SummaryResponse)
def create_summary(
    payload: schema.SummaryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Only writers can create summaries; writer_id is derived from token
    role = db.get(models.user_role.UserRole, current_user.role_id) if current_user.role_id else None
    if not role or role.name.lower() != "writer":
        raise HTTPException(status_code=403, detail="User is not a writer")
    item = models.summary.Summary(
        title=payload.title,
        content=payload.content,
        category_id=payload.category_id,
        writer_id=current_user.user_id,
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
    db: Session = Depends(get_db),
    only_writer: bool = Query(True, description="Only summaries created by users with role 'writer'"),
):
    q = db.query(models.summary.Summary)
    if only_writer:
        q = (
            q.join(models.user.User, models.summary.Summary.writer_id == models.user.User.user_id)
             .join(models.user_role.UserRole, models.user.User.role_id == models.user_role.UserRole.role_id)
             .filter(models.user_role.UserRole.name.ilike("writer"))
        )
    return q.all()


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

