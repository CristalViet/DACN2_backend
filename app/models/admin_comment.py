from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class AdminComment(Base):
    __tablename__ = "admin_comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.summary_id"), nullable=False)
    text_content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("admin_comments.comment_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


