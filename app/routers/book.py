from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import book as schema

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=schema.BookResponse)
def create_book(payload: schema.BookCreate, db: Session = Depends(get_db)):
    item = models.book.Book(
        category_id=payload.category_id,
        author_id=payload.author_id,
        publisher_id=payload.publisher_id,
        title=payload.title,
        publish_date=payload.publish_date,
        cover_image=payload.cover_image,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.BookResponse])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.book.Book).all()


@router.get("/{book_id}", response_model=schema.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    return item


@router.put("/{book_id}", response_model=schema.BookResponse)
def update_book(book_id: int, payload: schema.BookUpdate, db: Session = Depends(get_db)):
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

