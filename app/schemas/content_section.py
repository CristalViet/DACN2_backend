from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SectionCreate(BaseModel):
    summary_id: int
    section_order: int
    title: str
    content: str
    audio_segment_url: str | None = None


class SectionUpdate(BaseModel):
    section_order: int | None = None
    title: str | None = None
    content: str | None = None
    audio_segment_url: str | None = None


class SectionResponse(BaseModel):
    section_id: int
    summary_id: int
    section_order: int
    title: str
    content: str
    audio_segment_url: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


