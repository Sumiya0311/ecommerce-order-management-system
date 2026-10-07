from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    sku: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    category_id: int
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    sku: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    category_id: int
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    is_active: bool = True


class ProductResponse(BaseModel):
    product_id: int
    name: str
    sku: str
    description: str | None
    category_id: int
    price: float
    stock_quantity: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)