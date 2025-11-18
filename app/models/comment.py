from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, Enum
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
import enum


class CommentAccess(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    access = Column(Enum(CommentAccess), default=CommentAccess.PUBLIC)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    summary = relationship("Summary", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")
