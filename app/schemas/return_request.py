from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


class ReturnReject(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=5,
        max_length=500
    )


class ReturnResponse(BaseModel):
    return_id: int
    order_id: int
    reason: str
    status: str
    refund_amount: float | None
    rejection_reason: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)