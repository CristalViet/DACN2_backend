from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.comment import CommentAccess


class CommentCreate(BaseModel):
    summary_id: int
    content: str
    parent_comment_id: int | None = None
    access: CommentAccess = CommentAccess.PUBLIC


class CommentUpdate(BaseModel):
    content: str | None = None
    access: CommentAccess | None = None


class CommentResponse(BaseModel):
    id: int
    summary_id: int
    user_id: int
    content: str
    parent_comment_id: int | None
    access: CommentAccess
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


