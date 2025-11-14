from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship


class ContentSection(Base):
    __tablename__ = "content_sections"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False)
    section_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    audio_segment_url = Column(String(500), nullable=True)

    summary = relationship("Summary", back_populates="content_sections")


