from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import cart as schema
from app.core.deps import get_current_user

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.post("/", response_model=schema.CartResponse)
def create_cart(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a cart for the current user"""
    # Check if user already has a cart
    existing_cart = db.query(models.cart.Cart).filter(
        models.cart.Cart.user_id == current_user.id
    ).first()
    if existing_cart:
        raise HTTPException(status_code=400, detail="User already has a cart")
    
    item = models.cart.Cart(user_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/me", response_model=schema.CartResponse)
def get_my_cart(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's cart"""
    item = db.query(models.cart.Cart).filter(
        models.cart.Cart.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
    return item


@router.get("/{cart_id}", response_model=schema.CartResponse)
def get_cart(
    cart_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific cart by ID (only if it belongs to current user)"""
    item = db.get(models.cart.Cart, cart_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Check if cart belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this cart"
        )
    
    return item


@router.delete("/{cart_id}")
def delete_cart(
    cart_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a cart (only if it belongs to current user)"""
    item = db.get(models.cart.Cart, cart_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Check if cart belongs to current user
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this cart"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}

