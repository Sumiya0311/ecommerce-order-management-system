from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import (
    create_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def add_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return create_product(db, product_data)


@router.get(
    "",
    response_model=list[ProductResponse]
)
def list_products(
    name: str | None = Query(None),
    category_id: int | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    in_stock: bool | None = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer", "Admin"))
):
    return get_products(
        db=db,
        name=name,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer", "Admin"))
):
    return get_product(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def edit_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return update_product(db, product_id, product_data)


@router.delete(
    "/{product_id}"
)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return delete_product(db, product_id)