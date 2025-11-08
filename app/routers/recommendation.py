from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import recommendation as schema

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=schema.RecommendationResponse)
def create_recommendation(payload: schema.RecommendationCreate, db: Session = Depends(get_db)):
    item = models.recommendation.Recommendation(
        user_id=payload.user_id,
        recommended_summary_id=payload.recommended_summary_id,
        score=payload.score or 0,
        algorithm_type=payload.algorithm_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.RecommendationResponse])
def list_recommendations(db: Session = Depends(get_db)):
    return db.query(models.recommendation.Recommendation).all()


@router.get("/{recommendation_id}", response_model=schema.RecommendationResponse)
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    item = db.get(models.recommendation.Recommendation, recommendation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return item


@router.put("/{recommendation_id}", response_model=schema.RecommendationResponse)
def update_recommendation(recommendation_id: int, payload: schema.RecommendationUpdate, db: Session = Depends(get_db)):
    item = db.get(models.recommendation.Recommendation, recommendation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{recommendation_id}")
def delete_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    item = db.get(models.recommendation.Recommendation, recommendation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


