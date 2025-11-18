from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    category_name: str


class CategoryUpdate(BaseModel):
    category_name: str | None = None


class CategoryResponse(BaseModel):
    id: int
    category_name: str

    model_config = ConfigDict(from_attributes=True)


