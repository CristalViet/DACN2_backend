from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RatingCreate(BaseModel):
    user_id: int
    summary_id: int
    score: float


class RatingUpdate(BaseModel):
    score: float | None = None


class RatingResponse(BaseModel):
    rating_id: int
    user_id: int
    summary_id: int
    score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


