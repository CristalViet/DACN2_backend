from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal


class BookCreate(BaseModel):
    category_id: int | None = None
    author_id: int | None = None
    publisher_id: int | None = None
    title: str
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal
    stock_quantity: int = 0


class BookUpdate(BaseModel):
    category_id: int | None = None
    author_id: int | None = None
    publisher_id: int | None = None
    title: str | None = None
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None


class BookResponse(BaseModel):
    id: int
    category_id: int | None = None
    author_id: int | None = None
    publisher_id: int | None = None
    title: str
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal
    stock_quantity: int = 0

    model_config = ConfigDict(from_attributes=True)

