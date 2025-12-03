from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app import models
from app.schemas import favourite as schema
from app.core.deps import get_current_user
from app.models.summary import Summary
from app.models.book import Book
from app.models.favourite import Favourite

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.post("/", response_model=schema.FavouriteResponse)
def create_favourite(
    payload: schema.FavouriteCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a summary to favourites (Authenticated users only)"""
    # Check if summary exists
    summary = db.get(models.summary.Summary, payload.summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # Check if favourite already exists
    existing_favourite = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.summary_id == payload.summary_id
    ).first()
    
    if existing_favourite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary is already in favourites"
        )
    
    item = Favourite(
        user_id=current_user.id,
        summary_id=payload.summary_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Load summary with relations
    item = db.query(Favourite).options(
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.categories),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.authors),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Favourite.summary).selectinload(Summary.user)
    ).filter(Favourite.id == item.id).first()
    
    return item


@router.get("/me", response_model=list[schema.FavouriteResponse])
def get_my_favourites(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all favourites for the current user (Authenticated users only)"""
    favourites = db.query(Favourite).options(
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.categories),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.authors),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Favourite.summary).selectinload(Summary.user)
    ).filter(
        Favourite.user_id == current_user.id
    ).order_by(Favourite.created_at.desc()).all()
    
    return favourites


@router.get("/{favourite_id}", response_model=schema.FavouriteResponse)
def get_favourite(
    favourite_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific favourite (only if it belongs to current user)"""
    item = db.query(Favourite).options(
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.categories),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.authors),
        selectinload(Favourite.summary).selectinload(Summary.book).selectinload(Book.publisher),
        selectinload(Favourite.summary).selectinload(Summary.user)
    ).filter(Favourite.id == favourite_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Favourite not found")
    
    # Check if favourite belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this favourite"
        )
    
    return item


@router.delete("/{favourite_id}")
def delete_favourite(
    favourite_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a favourite (only if it belongs to current user)"""
    item = db.get(Favourite, favourite_id)
    if not item:
        raise HTTPException(status_code=404, detail="Favourite not found")
    
    # Check if favourite belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this favourite"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/check", response_model=dict)
def check_favourite(
    summary_id: int = Query(..., description="Summary ID to check"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a summary is in the current user's favourites"""
    item = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.summary_id == summary_id
    ).first()
    
    return {"is_favourite": item is not None}


@router.delete("/summary/{summary_id}")
def delete_favourite_by_summary(
    summary_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a favourite by summary_id (only if it belongs to current user)"""
    item = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.summary_id == summary_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Favourite not found")
    
    db.delete(item)
    db.commit()
    return {"deleted": True}

