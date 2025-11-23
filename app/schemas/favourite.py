from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.summary import SummaryResponse


class FavouriteCreate(BaseModel):
    summary_id: int


class FavouriteResponse(BaseModel):
    id: int
    user_id: int
    summary_id: int
    created_at: datetime
    summary: SummaryResponse | None = None

    model_config = ConfigDict(from_attributes=True)

