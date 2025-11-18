from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import cart_item as schema
from app.core.deps import get_current_user

router = APIRouter(prefix="/cart-items", tags=["Cart Items"])


@router.post("/", response_model=schema.CartItemResponse)
def create_cart_item(
    payload: schema.CartItemCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to the current user's cart"""
    # Get or create cart for current user
    cart = db.query(models.cart.Cart).filter(
        models.cart.Cart.user_id == current_user.id
    ).first()
    
    if not cart:
        # Create cart if it doesn't exist
        cart = models.cart.Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Check if book exists
    book = db.get(models.book.Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if item already exists in cart
    existing_item = db.query(models.cart_item.CartItem).filter(
        models.cart_item.CartItem.cart_id == cart.id,
        models.cart_item.CartItem.book_id == payload.book_id
    ).first()
    
    if existing_item:
        # Update quantity and price
        existing_item.quantity += payload.quantity
        existing_item.price = payload.price
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    item = models.cart_item.CartItem(
        cart_id=cart.id,
        book_id=payload.book_id,
        quantity=payload.quantity,
        price=payload.price,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/me", response_model=list[schema.CartItemResponse])
def get_my_cart_items(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cart items for the current user"""
    cart = db.query(models.cart.Cart).filter(
        models.cart.Cart.user_id == current_user.id
    ).first()
    
    if not cart:
        return []
    
    return db.query(models.cart_item.CartItem).filter(
        models.cart_item.CartItem.cart_id == cart.id
    ).all()


@router.get("/{cart_item_id}", response_model=schema.CartItemResponse)
def get_cart_item(
    cart_item_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific cart item (only if it belongs to current user's cart)"""
    item = db.get(models.cart_item.CartItem, cart_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check if cart item belongs to current user's cart
    cart = db.get(models.cart.Cart, item.cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this cart item"
        )
    
    return item


@router.put("/{cart_item_id}", response_model=schema.CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    payload: schema.CartItemUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a cart item (only if it belongs to current user's cart)"""
    item = db.get(models.cart_item.CartItem, cart_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check if cart item belongs to current user's cart
    cart = db.get(models.cart.Cart, item.cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this cart item"
        )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{cart_item_id}")
def delete_cart_item(
    cart_item_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a cart item (only if it belongs to current user's cart)"""
    item = db.get(models.cart_item.CartItem, cart_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check if cart item belongs to current user's cart
    cart = db.get(models.cart.Cart, item.cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this cart item"
        )
    
    db.delete(item)
    db.commit()
    return {"deleted": True}

