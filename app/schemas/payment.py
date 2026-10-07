from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: Literal["UPI", "Card", "Net Banking", "COD"]
    transaction_id: str = Field(
        ...,
        min_length=3,
        max_length=100
    )
    status: Literal["Success", "Failed"]


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)