from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import vocabulary as schema

router = APIRouter(prefix="/flashcards", tags=["Vocabulary"])


@router.post("/", response_model=schema.FlashcardResponse)
def create_flashcard(payload: schema.FlashcardCreate, db: Session = Depends(get_db)):
    item = models.vocabulary.VocabularyFlashcard(
        user_id=payload.user_id,
        word=payload.word,
        meaning=payload.meaning,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.FlashcardResponse])
def list_flashcards(db: Session = Depends(get_db)):
    return db.query(models.vocabulary.VocabularyFlashcard).all()


@router.get("/{flashcard_id}", response_model=schema.FlashcardResponse)
def get_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    item = db.get(models.vocabulary.VocabularyFlashcard, flashcard_id)
    if not item:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return item


@router.put("/{flashcard_id}", response_model=schema.FlashcardResponse)
def update_flashcard(flashcard_id: int, payload: schema.FlashcardUpdate, db: Session = Depends(get_db)):
    item = db.get(models.vocabulary.VocabularyFlashcard, flashcard_id)
    if not item:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{flashcard_id}")
def delete_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    item = db.get(models.vocabulary.VocabularyFlashcard, flashcard_id)
    if not item:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


