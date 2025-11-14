from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SummaryCreate(BaseModel):
    title: str
    book_author: str | None = None
    book_cover_path: str | None = None
    published_date: datetime | None = None
    category_id: int | None = None
    status: str | None = None
    audio_url: str | None = None


class SummaryUpdate(BaseModel):
    title: str | None = None
    book_author: str | None = None
    book_cover_path: str | None = None
    published_date: datetime | None = None
    category_id: int | None = None
    status: str | None = None
    avg_rating: float | None = None
    read_count: int | None = None
    audio_url: str | None = None


class SummaryResponse(BaseModel):
    id: int
    title: str
    book_author: str | None = None
    book_cover_path: str | None = None
    published_date: datetime | None = None
    category_id: int | None = None
    user_id: int | None = None
    status: str | None = None
    avg_rating: float = 0
    read_count: int = 0
    audio_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


