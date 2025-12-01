from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import order as schema
from app.core.deps import get_current_user, require_admin

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schema.OrderResponse)
def create_order(
    payload: schema.OrderCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order for the current user"""
    item = models.order.Order(
        user_id=current_user.id,
        total_amount=payload.total_amount,
        payment_method=payload.payment_method,
        payment_status=payload.payment_status,
        recipient_name=payload.recipient_name,
        address=payload.address,
        phone=payload.phone,
        shipment_status=payload.shipment_status,
        delivery_date=payload.delivery_date,
        shipping_method=payload.shipping_method,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.OrderResponse])
def list_orders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user"""
    return db.query(models.order.Order).filter(
        models.order.Order.user_id == current_user.id
    ).all()


@router.get("/admin", response_model=list[schema.OrderResponse])
def list_all_orders_admin(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all orders in the system (Admin only).
    """
    return db.query(models.order.Order).all()


@router.get("/admin/{order_id}", response_model=schema.OrderResponse)
def get_order_admin(
    order_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by ID for admin (shortcut route).
    """
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    return item


@router.get("/{order_id}", response_model=schema.OrderResponse)
def get_order(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by ID.
    - Normal user: only if the order belongs to them.
    - Admin: can access any order.
    """
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check ownership for normal users; admins can access all orders
    if item.user_id != current_user.id and (
        not current_user.role or current_user.role.role_name != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    return item


@router.put("/{order_id}", response_model=schema.OrderResponse)
def update_order(
    order_id: int,
    payload: schema.UserOrderUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an order (only if it belongs to current user).
    Normal users can only edit contact/shipping info, not payment/shipment status.
    """
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/admin/{order_id}", response_model=schema.OrderResponse)
def admin_update_order(
    order_id: int,
    payload: schema.OrderUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to update an order.
    Admin can change payment_status, shipment_status, and other order fields.
    """
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an order (only if it belongs to current user)"""
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this order"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.patch("/{order_id}/payment-status", response_model=schema.OrderResponse)
def update_payment_status(
    order_id: int,
    payload: schema.PaymentStatusUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update payment status of an order (Admin only)"""
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item.payment_status = payload.payment_status
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{order_id}/shipment-status", response_model=schema.OrderResponse)
def update_shipment_status(
    order_id: int,
    payload: schema.ShipmentStatusUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update shipment status of an order (Admin only)"""
    item = db.get(models.order.Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item.shipment_status = payload.shipment_status
    db.commit()
    db.refresh(item)
    return item

