from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from app.services.cart_service import (
    add_cart_item,
    clear_cart,
    delete_cart_item,
    get_cart,
    update_cart_item,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.get(
    "",
    response_model=CartResponse
)
def view_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_cart(db, current_user.user_id)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return add_cart_item(
        db,
        current_user.user_id,
        item_data
    )



@router.put(
    "/items/{cart_item_id}",
    response_model=CartResponse
)
def update_item(
    cart_item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return update_cart_item(
        db,
        current_user.user_id,
        cart_item_id,
        item_data
    )



@router.delete(
    "/items/{cart_item_id}",
    response_model=CartResponse
)
def remove_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return delete_cart_item(
        db,
        current_user.user_id,
        cart_item_id
    )


@router.delete(
    "",
    status_code=status.HTTP_200_OK
)
def remove_all_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return clear_cart(
        db,
        current_user.user_id
    )