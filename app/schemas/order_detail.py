from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class OrderDetailCreate(BaseModel):
    order_id: int
    book_id: int
    quantity: int
    price: Decimal


class OrderDetailUpdate(BaseModel):
    quantity: int | None = None
    price: Decimal | None = None


class OrderDetailResponse(BaseModel):
    id: int
    order_id: int
    book_id: int
    quantity: int
    price: Decimal

    model_config = ConfigDict(from_attributes=True)

