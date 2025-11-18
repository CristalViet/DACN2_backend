from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class CartItemCreate(BaseModel):
    book_id: int
    quantity: int
    price: Decimal


class CartItemUpdate(BaseModel):
    quantity: int | None = None
    price: Decimal | None = None


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    book_id: int
    quantity: int
    price: Decimal

    model_config = ConfigDict(from_attributes=True)

