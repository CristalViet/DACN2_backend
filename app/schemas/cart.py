from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CartCreate(BaseModel):
    pass  # user_id will be taken from token


class CartResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

