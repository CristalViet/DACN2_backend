from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import rating as schema

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/", response_model=schema.RatingResponse)
def create_rating(payload: schema.RatingCreate, db: Session = Depends(get_db)):
    item = models.rating.Rating(
        user_id=payload.user_id,
        summary_id=payload.summary_id,
        score=payload.score,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.RatingResponse])
def list_ratings(db: Session = Depends(get_db)):
    return db.query(models.rating.Rating).all()


@router.get("/{rating_id}", response_model=schema.RatingResponse)
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    item = db.get(models.rating.Rating, rating_id)
    if not item:
        raise HTTPException(status_code=404, detail="Rating not found")
    return item


@router.put("/{rating_id}", response_model=schema.RatingResponse)
def update_rating(rating_id: int, payload: schema.RatingUpdate, db: Session = Depends(get_db)):
    item = db.get(models.rating.Rating, rating_id)
    if not item:
        raise HTTPException(status_code=404, detail="Rating not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    item = db.get(models.rating.Rating, rating_id)
    if not item:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


