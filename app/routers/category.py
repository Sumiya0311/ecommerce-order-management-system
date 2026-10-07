from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import (
    create_category,
    delete_category,
    get_categories,
    update_category,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def add_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return create_category(db, category_data)


@router.get(
    "",
    response_model=list[CategoryResponse]
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return get_categories(db)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def edit_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return update_category(db, category_id, category_data)


@router.delete(
    "/{category_id}"
)
def remove_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return delete_category(db, category_id)