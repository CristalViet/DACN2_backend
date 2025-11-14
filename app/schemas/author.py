from pydantic import BaseModel, ConfigDict
from datetime import date


class AuthorCreate(BaseModel):
    name: str
    birth_date: date | None = None
    nationality: str | None = None
    biography: str | None = None


class AuthorUpdate(BaseModel):
    name: str | None = None
    birth_date: date | None = None
    nationality: str | None = None
    biography: str | None = None


class AuthorResponse(BaseModel):
    id: int
    name: str
    birth_date: date | None = None
    nationality: str | None = None
    biography: str | None = None

    model_config = ConfigDict(from_attributes=True)

