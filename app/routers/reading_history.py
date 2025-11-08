from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import reading_history as schema

router = APIRouter(prefix="/reading-history", tags=["ReadingHistory"])


@router.post("/", response_model=schema.ReadingHistoryResponse)
def create_reading_history(payload: schema.ReadingHistoryCreate, db: Session = Depends(get_db)):
    item = models.reading_history.ReadingHistory(
        user_id=payload.user_id,
        summary_id=payload.summary_id,
        last_section_id=payload.last_section_id,
        progress_percent=payload.progress_percent or 0,
        time_spent=payload.time_spent or 0,
        device_type=payload.device_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.ReadingHistoryResponse])
def list_reading_history(db: Session = Depends(get_db)):
    return db.query(models.reading_history.ReadingHistory).all()


@router.get("/{reading_id}", response_model=schema.ReadingHistoryResponse)
def get_reading_history(reading_id: int, db: Session = Depends(get_db)):
    item = db.get(models.reading_history.ReadingHistory, reading_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    return item


@router.put("/{reading_id}", response_model=schema.ReadingHistoryResponse)
def update_reading_history(reading_id: int, payload: schema.ReadingHistoryUpdate, db: Session = Depends(get_db)):
    item = db.get(models.reading_history.ReadingHistory, reading_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{reading_id}")
def delete_reading_history(reading_id: int, db: Session = Depends(get_db)):
    item = db.get(models.reading_history.ReadingHistory, reading_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reading history not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


