from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import order_detail as schema

router = APIRouter(prefix="/order-details", tags=["Order Details"])


@router.post("/", response_model=schema.OrderDetailResponse)
def create_order_detail(payload: schema.OrderDetailCreate, db: Session = Depends(get_db)):
    item = models.order_detail.OrderDetail(
        order_id=payload.order_id,
        book_id=payload.book_id,
        quantity=payload.quantity,
        price=payload.price,
    )
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
    item = db.get(models.order_detail.OrderDetail, order_detail_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order detail not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{order_detail_id}")
def delete_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    item = db.get(models.order_detail.OrderDetail, order_detail_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order detail not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

