from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import content_section as schema

router = APIRouter(prefix="/content-sections", tags=["Content Sections"])


@router.post("/", response_model=schema.ContentSectionResponse)
def create_content_section(payload: schema.ContentSectionCreate, db: Session = Depends(get_db)):
    item = models.content_section.ContentSection(
        summary_id=payload.summary_id,
        section_order=payload.section_order,
        title=payload.title,
        content=payload.content,
        audio_segment_url=payload.audio_segment_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.ContentSectionResponse])
def list_content_sections(db: Session = Depends(get_db)):
    return db.query(models.content_section.ContentSection).all()


@router.get("/{content_section_id}", response_model=schema.ContentSectionResponse)
def get_content_section(content_section_id: int, db: Session = Depends(get_db)):
    item = db.get(models.content_section.ContentSection, content_section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content section not found")
    return item


@router.put("/{content_section_id}", response_model=schema.ContentSectionResponse)
def update_content_section(content_section_id: int, payload: schema.ContentSectionUpdate, db: Session = Depends(get_db)):
    item = db.get(models.content_section.ContentSection, content_section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content section not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{content_section_id}", response_model=schema.ContentSectionResponse)
def patch_content_section(content_section_id: int, payload: schema.ContentSectionUpdate, db: Session = Depends(get_db)):
    item = db.get(models.content_section.ContentSection, content_section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content section not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/sections-order")
def reorder_content_sections(payload: schema.ContentSectionReorder, db: Session = Depends(get_db)):
    # Update section_order for each ID based on its position in the array
    for index, section_id in enumerate(payload.order, start=1):
        item = db.get(models.content_section.ContentSection, section_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Content section with id {section_id} not found")
        item.section_order = index
    db.commit()
    return {"message": "Sections reordered successfully", "order": payload.order}


@router.delete("/{content_section_id}")
def delete_content_section(content_section_id: int, db: Session = Depends(get_db)):
    item = db.get(models.content_section.ContentSection, content_section_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content section not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

