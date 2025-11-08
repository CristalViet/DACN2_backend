from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RecommendationCreate(BaseModel):
    user_id: int
    recommended_summary_id: int
    score: float | None = None
    algorithm_type: str | None = None


class RecommendationUpdate(BaseModel):
    score: float | None = None
    algorithm_type: str | None = None


class RecommendationResponse(BaseModel):
    recommendation_id: int
    user_id: int
    recommended_summary_id: int
    score: float
    algorithm_type: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


