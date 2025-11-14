from pydantic import BaseModel, ConfigDict


class ContentSectionCreate(BaseModel):
    summary_id: int
    section_order: int
    title: str | None = None
    content: str | None = None
    audio_segment_url: str | None = None


class ContentSectionUpdate(BaseModel):
    section_order: int | None = None
    title: str | None = None
    content: str | None = None
    audio_segment_url: str | None = None


class ContentSectionResponse(BaseModel):
    id: int
    summary_id: int
    section_order: int
    title: str | None = None
    content: str | None = None
    audio_segment_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

