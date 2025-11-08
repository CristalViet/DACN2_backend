from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class NoteHighlight(Base):
    __tablename__ = "notes_highlights"

    note_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    summary_id = Column(Integer, ForeignKey("summaries.summary_id"))
    section_id = Column(Integer, nullable=True)
    highlighted_text = Column(Text)
    note_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
