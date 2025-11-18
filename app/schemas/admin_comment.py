from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AdminCommentCreate(BaseModel):
    summary_id: int
    text_content: str
    parent_comment_id: int | None = None


class AdminCommentUpdate(BaseModel):
    text_content: str | None = None


class AdminCommentResponse(BaseModel):
    id: int
    summary_id: int
    text_content: str
    parent_comment_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

