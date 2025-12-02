from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app import models
from app.schemas import author as schema
from app.core.deps import require_admin
from typing import Optional

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post("/", response_model=schema.AuthorResponse)
def create_author(
    payload: schema.AuthorCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new author (Admin only)"""
    item = models.author.Author(
        name=payload.name,
        birth_date=payload.birth_date,
        nationality=payload.nationality,
        biography=payload.biography,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.AuthorResponse])
def list_authors(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or biography"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
):
    """
    Get all authors with optional filters (Public access).
    Supports search by name/biography and filter by nationality.
    """
    query = db.query(models.author.Author)
    
    # Apply search filter
    if search:
        search_filter = or_(
            models.author.Author.name.ilike(f"%{search}%"),
            models.author.Author.biography.ilike(f"%{search}%") if models.author.Author.biography else False
        )
        query = query.filter(search_filter)
    
    # Apply nationality filter
    if nationality:
        query = query.filter(models.author.Author.nationality.ilike(f"%{nationality}%"))
    
    authors = query.order_by(models.author.Author.name).all()
    return authors


@router.get("/{author_id}", response_model=schema.AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    """Get a specific author (Public access)"""
    item = db.get(models.author.Author, author_id)
    if not item:
        raise HTTPException(status_code=404, detail="Author not found")
    return item


@router.put("/{author_id}", response_model=schema.AuthorResponse)
def update_author_put(
    author_id: int,
    payload: schema.AuthorUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an author (Admin only) - PUT method"""
    item = db.get(models.author.Author, author_id)
    if not item:
        raise HTTPException(status_code=404, detail="Author not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{author_id}", response_model=schema.AuthorResponse)
def update_author(
    author_id: int,
    payload: schema.AuthorUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an author (Admin only) - PATCH method"""
    item = db.get(models.author.Author, author_id)
    if not item:
        raise HTTPException(status_code=404, detail="Author not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{author_id}")
def delete_author(
    author_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an author (Admin only)"""
    item = db.get(models.author.Author, author_id)
    if not item:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

