from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import author as schema
from app.core.deps import require_admin

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
def list_authors(db: Session = Depends(get_db)):
    """Get all authors (Public access)"""
    return db.query(models.author.Author).all()


@router.get("/{author_id}", response_model=schema.AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    """Get a specific author (Public access)"""
    item = db.get(models.author.Author, author_id)
    if not item:
        raise HTTPException(status_code=404, detail="Author not found")
    return item


@router.put("/{author_id}", response_model=schema.AuthorResponse)
def update_author(
    author_id: int,
    payload: schema.AuthorUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an author (Admin only)"""
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

