# app/models/favorite.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Favourite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    summary = relationship("Summary", backref="favourites")

