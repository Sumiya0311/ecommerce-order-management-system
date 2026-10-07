from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    cart_item_id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    line_total: float


class CartResponse(BaseModel):
    cart_id: int
    items: list[CartItemResponse]
    subtotal: float