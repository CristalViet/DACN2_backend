from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str | None = None


class CategoryResponse(BaseModel):
    category_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


