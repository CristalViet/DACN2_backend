from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import note as schema

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=schema.NoteResponse)
def create_note(payload: schema.NoteCreate, db: Session = Depends(get_db)):
    item = models.note.NoteHighlight(
        user_id=payload.user_id,
        summary_id=payload.summary_id,
        section_id=payload.section_id,
        highlighted_text=payload.highlighted_text,
        note_content=payload.note_content,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.NoteResponse])
def list_notes(db: Session = Depends(get_db)):
    return db.query(models.note.NoteHighlight).all()


@router.get("/{note_id}", response_model=schema.NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    item = db.get(models.note.NoteHighlight, note_id)
    if not item:
        raise HTTPException(status_code=404, detail="Note not found")
    return item


@router.put("/{note_id}", response_model=schema.NoteResponse)
def update_note(note_id: int, payload: schema.NoteUpdate, db: Session = Depends(get_db)):
    item = db.get(models.note.NoteHighlight, note_id)
    if not item:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    item = db.get(models.note.NoteHighlight, note_id)
    if not item:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


