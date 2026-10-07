from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=500)


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=500)


class ReviewResponse(BaseModel):
    review_id: int
    product_id: int
    customer_id: int
    rating: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)