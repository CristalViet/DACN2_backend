from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from app.schemas.category import CategoryResponse
from app.schemas.author import AuthorResponse
from app.schemas.publisher import PublisherResponse
from app.schemas.user import UserResponse


class SummaryCreate(BaseModel):
    title: str
    content: str
    category_id: int


class SummaryUpdate(BaseModel):
    title: str | None = None
    book_id: int | None = None
    status: str | None = None
    avg_rating: float | None = None
    read_count: int | None = None
    audio_url: str | None = None


class BookWithRelationsResponse(BaseModel):
    id: int
    title: str
    publish_date: date | None = None
    cover_image: str | None = None
    price: Decimal
    stock_quantity: int = 0
    category: CategoryResponse | None = None
    author: AuthorResponse | None = None
    publisher: PublisherResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    id: int
    title: str
    book_id: int | None = None
    user_id: int | None = None
    status: str | None = None
    avg_rating: float = 0
    read_count: int = 0
    audio_url: str | None = None
    published_date: datetime | None = None
    created_at: datetime
    book: BookWithRelationsResponse | None = None
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


