from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ReadingHistoryCreate(BaseModel):
    user_id: int
    summary_id: int
    last_section_id: int | None = None
    progress_percent: float = 0
    time_spent: int = 0
    device_type: str | None = None


class ReadingHistoryUpdate(BaseModel):
    last_section_id: int | None = None
    progress_percent: float | None = None
    time_spent: int | None = None
    device_type: str | None = None


class ReadingHistoryResponse(BaseModel):
    reading_id: int
    user_id: int
    summary_id: int
    last_section_id: int | None
    progress_percent: float
    time_spent: int
    device_type: str | None
    last_read_date: datetime

    model_config = ConfigDict(from_attributes=True)


