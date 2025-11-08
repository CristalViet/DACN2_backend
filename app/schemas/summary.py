from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SummaryCreate(BaseModel):
    title: str
    content: str
    category_id: int
    writer_id: int


class SummaryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None


class SummaryResponse(BaseModel):
    summary_id: int
    title: str
    content: str
    category_id: int
    writer_id: int
    avg_rating: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


