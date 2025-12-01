from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import List
from app.schemas.category import CategoryResponse
from app.schemas.author import AuthorResponse
from app.schemas.publisher import PublisherResponse


class BookCreate(BaseModel):
    category_ids: List[int] = []
    author_ids: List[int] = []
    publisher_id: int | None = None
    title: str
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal
    stock_quantity: int = 0


class BookUpdate(BaseModel):
    category_ids: List[int] | None = None
    author_ids: List[int] | None = None
    publisher_id: int | None = None
    title: str | None = None
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None


class BookResponse(BaseModel):
    id: int
    publisher_id: int | None = None
    title: str
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal
    stock_quantity: int = 0
    categories: List[CategoryResponse] = []
    authors: List[AuthorResponse] = []
    publisher: PublisherResponse | None = None

    model_config = ConfigDict(from_attributes=True)

