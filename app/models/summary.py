from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base

class Summary(Base):
    __tablename__ = "summaries"

    summary_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    writer_id = Column(Integer, ForeignKey("users.user_id"))
    avg_rating = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
