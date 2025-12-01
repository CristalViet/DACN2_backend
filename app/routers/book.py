from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import book as schema
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=schema.BookResponse)
def create_book(payload: schema.BookCreate, db: Session = Depends(get_db)):
    item = models.book.Book(
        publisher_id=payload.publisher_id,
        title=payload.title,
        publish_date=payload.publish_date,
        cover_image=payload.cover_image,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
    )
    
    # Handle many-to-many relationships
    if payload.category_ids:
        categories = db.query(models.category.Category).filter(
            models.category.Category.id.in_(payload.category_ids)
        ).all()
        item.categories = categories
    
    if payload.author_ids:
        authors = db.query(models.author.Author).filter(
            models.author.Author.id.in_(payload.author_ids)
        ).all()
        item.authors = authors
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Load relationships
    item = db.query(models.book.Book).options(
        selectinload(models.book.Book.categories),
        selectinload(models.book.Book.authors),
        selectinload(models.book.Book.publisher),
    ).filter(models.book.Book.id == item.id).first()
    
    return item


@router.get("/", response_model=list[schema.BookResponse])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.book.Book).options(
        selectinload(models.book.Book.categories),
        selectinload(models.book.Book.authors),
        selectinload(models.book.Book.publisher),
    ).all()


@router.get("/available", response_model=list[schema.BookResponse])
def list_books_without_summary(db: Session = Depends(get_db)):
    """
    Return books that do not have any summaries yet.
    Useful for writers when selecting a book to summarize.
    """
    books_without_summaries = (
        db.query(models.book.Book)
        .options(
            selectinload(models.book.Book.categories),
            selectinload(models.book.Book.authors),
            selectinload(models.book.Book.publisher),
        )
        .outerjoin(
            models.summary.Summary,
            models.summary.Summary.book_id == models.book.Book.id,
        )
        .filter(models.summary.Summary.id.is_(None))
        .all()
    )
    return books_without_summaries


@router.get("/{book_id}", response_model=schema.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    item = db.query(models.book.Book).options(
        selectinload(models.book.Book.categories),
        selectinload(models.book.Book.authors),
        selectinload(models.book.Book.publisher),
    ).filter(models.book.Book.id == book_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    return item



@router.put("/{book_id}", response_model=schema.BookResponse)
def update_book(book_id: int, payload: schema.BookUpdate, db: Session = Depends(get_db)):
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Handle regular fields
    update_data = payload.model_dump(exclude_unset=True, exclude={'category_ids', 'author_ids'})
    for field, value in update_data.items():
        setattr(item, field, value)
    
    # Handle many-to-many relationships
    if payload.category_ids is not None:
        categories = db.query(models.category.Category).filter(
            models.category.Category.id.in_(payload.category_ids)
        ).all()
        item.categories = categories
    
    if payload.author_ids is not None:
        authors = db.query(models.author.Author).filter(
            models.author.Author.id.in_(payload.author_ids)
        ).all()
        item.authors = authors
    
    db.commit()
    db.refresh(item)
    
    # Load relationships
    item = db.query(models.book.Book).options(
        selectinload(models.book.Book.categories),
        selectinload(models.book.Book.authors),
        selectinload(models.book.Book.publisher),
    ).filter(models.book.Book.id == item.id).first()
    
    return item


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

