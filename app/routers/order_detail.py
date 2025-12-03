from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import order_detail as schema

router = APIRouter(prefix="/order-details", tags=["Order Details"])


@router.post("/", response_model=schema.OrderDetailResponse)
def create_order_detail(payload: schema.OrderDetailCreate, db: Session = Depends(get_db)):
    """
    Create order detail and decrease book stock accordingly.
    """
    book = db.get(models.book.Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.stock_quantity is None:
        book.stock_quantity = 0

    if book.stock_quantity < payload.quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock for this book",
        )

    # Create order detail
    item = models.order_detail.OrderDetail(
        order_id=payload.order_id,
        book_id=payload.book_id,
        quantity=payload.quantity,
        price=payload.price,
    )

    # Decrease stock
    book.stock_quantity -= payload.quantity

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.OrderDetailResponse])
def list_order_details(db: Session = Depends(get_db)):
    return db.query(models.order_detail.OrderDetail).all()


@router.get("/{order_detail_id}", response_model=schema.OrderDetailResponse)
def get_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    item = db.get(models.order_detail.OrderDetail, order_detail_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return item


@router.put("/{order_detail_id}", response_model=schema.OrderDetailResponse)
def update_order_detail(order_detail_id: int, payload: schema.OrderDetailUpdate, db: Session = Depends(get_db)):
    """
    Update order detail and adjust book stock based on quantity change.
    """
    item = db.get(models.order_detail.OrderDetail, order_detail_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order detail not found")

    original_quantity = item.quantity

    # Apply updates
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    # If quantity changed, adjust stock
    if "quantity" in update_data:
        new_quantity = item.quantity
        delta = new_quantity - original_quantity

        if delta != 0:
            book = db.get(models.book.Book, item.book_id)
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")

            if book.stock_quantity is None:
                book.stock_quantity = 0

            # delta > 0 means we need more items → decrease stock
            if delta > 0 and book.stock_quantity < delta:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough stock to increase quantity for this book",
                )

            book.stock_quantity -= delta

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{order_detail_id}")
def delete_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    """
    Delete order detail and return stock to book.
    """
    item = db.get(models.order_detail.OrderDetail, order_detail_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order detail not found")

    # Return stock
    book = db.get(models.book.Book, item.book_id)
    if book:
        if book.stock_quantity is None:
            book.stock_quantity = 0
        book.stock_quantity += item.quantity

    db.delete(item)
    db.commit()
    return {"deleted": True}

