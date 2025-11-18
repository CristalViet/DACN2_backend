from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.database import get_db
from app import models
from app.schemas import content_section as schema

router = APIRouter(prefix="/sections", tags=["Sections"])


@router.get("/by-summary/{summary_id}", response_model=list[schema.SectionResponse])
def list_sections_by_summary(
    summary_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = (
        db.query(models.content_section.ContentSection)
        .filter(models.content_section.ContentSection.summary_id == summary_id)
        .order_by(asc(models.content_section.ContentSection.section_order))
    )
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{section_id}", response_model=schema.SectionResponse)
def get_section(section_id: int, db: Session = Depends(get_db)):
    item = db.get(models.content_section.ContentSection, section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Section not found")
    return item


