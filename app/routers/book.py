from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query, Request
from fastapi import status as http_status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import book as schema
from sqlalchemy.orm import selectinload
from pathlib import Path
import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import date

router = APIRouter(prefix="/books", tags=["Books"])


async def save_book_image(file: UploadFile, request: Optional[Request] = None) -> str:
    """Helper function to save book cover image and return the full URL"""
    from app.helpers.url import get_full_image_url
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("static/uploads/books")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Return full URL for database storage (auto-detect from request if available)
        relative_path = f"/static/uploads/books/{filename}"
        return get_full_image_url(relative_path, request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )


def delete_book_image(image_url: Optional[str]):
    """Helper function to delete book cover image"""
    if image_url:
        # Extract relative path from full URL if needed
        if image_url.startswith(("http://", "https://")):
            # Extract path from full URL
            from urllib.parse import urlparse
            parsed = urlparse(image_url)
            relative_path = parsed.path
        else:
            relative_path = image_url
        
        # Remove leading slash and get file path
        old_image_path = Path("static") / relative_path.lstrip("/")
        if old_image_path.exists():
            try:
                old_image_path.unlink()
            except Exception:
                pass  # Ignore errors when deleting old images


@router.post("/", response_model=schema.BookResponse)
async def create_book(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create a new book with optional cover image upload.
    Supports both JSON and FormData (multipart/form-data).
    """
    content_type = request.headers.get("content-type", "")
    
    if "multipart/form-data" in content_type:
        # Handle FormData request
        form_data = await request.form()
        
        title = form_data.get("title")
        if not title:
            raise HTTPException(status_code=400, detail="title is required")
        
        price_str = form_data.get("price")
        if not price_str:
            raise HTTPException(status_code=400, detail="price is required")
        try:
            price = Decimal(price_str)
        except:
            raise HTTPException(status_code=400, detail="Invalid price format")
        
        stock_quantity = int(form_data.get("stock_quantity", 0) or 0)
        publisher_id = form_data.get("publisher_id")
        publisher_id = int(publisher_id) if publisher_id else None
        
        publish_date_str = form_data.get("publish_date")
        publish_date = None
        if publish_date_str:
            try:
                publish_date = date.fromisoformat(publish_date_str)
            except:
                pass
        
        # Handle arrays
        category_ids = [int(id) for id in form_data.getlist("category_ids") if id]
        author_ids = [int(id) for id in form_data.getlist("author_ids") if id]
        
        # Handle image upload
        cover_image_url = None
        cover_image = form_data.get("cover_image")
        if cover_image and hasattr(cover_image, 'filename') and cover_image.filename:
            cover_image_url = await save_book_image(cover_image, request)
        
        item = models.book.Book(
            publisher_id=publisher_id,
            title=title,
            publish_date=publish_date,
            cover_image=cover_image_url,
            price=price,
            stock_quantity=stock_quantity,
        )
        
        # Handle many-to-many relationships
        if category_ids:
            categories = db.query(models.category.Category).filter(
                models.category.Category.id.in_(category_ids)
            ).all()
            item.categories = categories
        
        if author_ids:
            authors = db.query(models.author.Author).filter(
                models.author.Author.id.in_(author_ids)
            ).all()
            item.authors = authors
    else:
        # Handle JSON request
        try:
            payload_data = await request.json()
            payload = schema.BookCreate(**payload_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
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
async def update_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a book with optional cover image upload. Supports both JSON and FormData."""
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    
    content_type = request.headers.get("content-type", "")
    
    if "multipart/form-data" in content_type:
        # Handle FormData request
        form_data = await request.form()
        
        # Handle image upload
        cover_image = form_data.get("cover_image")
        if cover_image and hasattr(cover_image, 'filename') and cover_image.filename:
            # Delete old image if exists
            delete_book_image(item.cover_image)
            # Save new image
            item.cover_image = await save_book_image(cover_image, request)
        
        # Handle regular fields
        if "title" in form_data:
            item.title = form_data.get("title")
        if "price" in form_data:
            price_str = form_data.get("price")
            if price_str:
                try:
                    item.price = Decimal(price_str)
                except:
                    pass
        if "stock_quantity" in form_data:
            stock_str = form_data.get("stock_quantity")
            if stock_str:
                try:
                    item.stock_quantity = int(stock_str)
                except:
                    pass
        if "publisher_id" in form_data:
            pub_id = form_data.get("publisher_id")
            item.publisher_id = int(pub_id) if pub_id else None
        if "publish_date" in form_data:
            date_str = form_data.get("publish_date")
            if date_str:
                try:
                    item.publish_date = date.fromisoformat(date_str)
                except:
                    pass
        
        # Handle many-to-many relationships
        if "category_ids" in form_data:
            category_ids = [int(id) for id in form_data.getlist("category_ids") if id]
            categories = db.query(models.category.Category).filter(
                models.category.Category.id.in_(category_ids)
            ).all()
            item.categories = categories
        
        if "author_ids" in form_data:
            author_ids = [int(id) for id in form_data.getlist("author_ids") if id]
            authors = db.query(models.author.Author).filter(
                models.author.Author.id.in_(author_ids)
            ).all()
            item.authors = authors
    else:
        # Handle JSON request
        try:
            payload_data = await request.json()
            payload = schema.BookUpdate(**payload_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
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


@router.patch("/{book_id}", response_model=schema.BookResponse)
async def patch_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Partially update a book with optional cover image upload (same as PUT)"""
    return await update_book(book_id=book_id, request=request, db=db)


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book and its cover image"""
    item = db.get(models.book.Book, book_id)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete cover image if exists
    delete_book_image(item.cover_image)
    
    db.delete(item)
    db.commit()
    return {"deleted": True}

