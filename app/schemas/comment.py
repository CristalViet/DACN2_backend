from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CommentCreate(BaseModel):
    user_id: int
    summary_id: int
    content: str
    parent_comment_id: int | None = None


class CommentUpdate(BaseModel):
    content: str | None = None


class CommentResponse(BaseModel):
    comment_id: int
    user_id: int
    summary_id: int
    content: str
    parent_comment_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


