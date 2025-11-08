from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import summary as schema

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/", response_model=schema.SummaryResponse)
def create_summary(payload: schema.SummaryCreate, db: Session = Depends(get_db)):
    # Optional: validate foreign keys exist
    item = models.summary.Summary(
        title=payload.title,
        content=payload.content,
        category_id=payload.category_id,
        writer_id=payload.writer_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.SummaryResponse])
def list_summaries(db: Session = Depends(get_db)):
    return db.query(models.summary.Summary).all()


@router.get("/{summary_id}", response_model=schema.SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    return item


@router.put("/{summary_id}", response_model=schema.SummaryResponse)
def update_summary(summary_id: int, payload: schema.SummaryUpdate, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{summary_id}")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


