from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class CategoryUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    category_id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)