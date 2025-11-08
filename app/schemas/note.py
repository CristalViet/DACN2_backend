from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NoteCreate(BaseModel):
    user_id: int
    summary_id: int
    section_id: int | None = None
    highlighted_text: str | None = None
    note_content: str | None = None


class NoteUpdate(BaseModel):
    section_id: int | None = None
    highlighted_text: str | None = None
    note_content: str | None = None


class NoteResponse(BaseModel):
    note_id: int
    user_id: int
    summary_id: int
    section_id: int | None
    highlighted_text: str | None
    note_content: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


