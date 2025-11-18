from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), nullable=True)
    avg_rating = Column(Float, default=0)
    read_count = Column(Integer, default=0)
    audio_url = Column(String(500), nullable=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    book = relationship("Book", back_populates="summaries")
    user = relationship("User", back_populates="summaries")
    content_sections = relationship("ContentSection", back_populates="summary")
    comments = relationship("Comment", back_populates="summary")
    admin_comments = relationship("AdminComment", back_populates="summary")
