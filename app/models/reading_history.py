from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String
from sqlalchemy.sql import func
from app.database import Base

class ReadingHistory(Base):
    __tablename__ = "reading_history"

    reading_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    summary_id = Column(Integer, ForeignKey("summaries.id"))
    last_section_id = Column(Integer, nullable=True)
    progress_percent = Column(Float, default=0)
    time_spent = Column(Integer, default=0)
    device_type = Column(String(50))
    last_read_date = Column(DateTime(timezone=True), server_default=func.now())
