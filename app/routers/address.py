from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from app.services.address_service import (
    create_address,
    get_addresses,
    update_address,
    delete_address,
    set_default_address,
)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


# 1. POST /addresses
@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED
)
def add_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return create_address(
        db,
        current_user.user_id,
        address_data
    )


# 2. GET /addresses
@router.get(
    "",
    response_model=list[AddressResponse]
)
def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_addresses(
        db,
        current_user.user_id
    )


# 3. PUT /addresses/{address_id}/default
@router.put(
    "/{address_id}/default",
    response_model=AddressResponse
)
def make_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return set_default_address(
        db,
        current_user.user_id,
        address_id
    )


# 4. PUT /addresses/{address_id}
@router.put(
    "/{address_id}",
    response_model=AddressResponse
)
def edit_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return update_address(
        db,
        current_user.user_id,
        address_id,
        address_data
    )


# 5. DELETE /addresses/{address_id}
@router.delete(
    "/{address_id}"
)
def remove_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return delete_address(
        db,
        current_user.user_id,
        address_id
    )