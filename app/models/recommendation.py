from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    recommended_summary_id = Column(Integer, ForeignKey("summaries.summary_id"))
    score = Column(Float, default=0)
    algorithm_type = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
