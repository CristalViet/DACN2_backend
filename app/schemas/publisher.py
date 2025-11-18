from pydantic import BaseModel, ConfigDict


class PublisherCreate(BaseModel):
    name: str


class PublisherUpdate(BaseModel):
    name: str | None = None


class PublisherResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

