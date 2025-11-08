from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FlashcardCreate(BaseModel):
    user_id: int
    word: str
    meaning: str


class FlashcardUpdate(BaseModel):
    word: str | None = None
    meaning: str | None = None
    review_count: int | None = None
    last_reviewed: datetime | None = None


class FlashcardResponse(BaseModel):
    flashcard_id: int
    user_id: int
    word: str
    meaning: str
    created_at: datetime
    last_reviewed: datetime | None
    review_count: int

    model_config = ConfigDict(from_attributes=True)


