from pydantic import BaseModel, ConfigDict, Field


class OrderItemResponse(BaseModel):
    order_item_id: int
    product_id: int
    quantity: int
    unit_price: float
    line_total: float

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    address_id: int


class OrderResponse(BaseModel):
    order_id: int
    order_number: str
    customer_id: int
    address_id: int
    subtotal: float
    tax_amount: float
    delivery_charge: float
    grand_total: float
    status: str
    payment_status: str
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern=r"^(Confirmed|Shipped|Delivered)$"
    )