from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class AdminComment(Base):
    __tablename__ = "admin_comments"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False)
    text_content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("admin_comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    summary = relationship("Summary", back_populates="admin_comments")
    parent_comment = relationship("AdminComment", remote_side=[id], backref="replies")


