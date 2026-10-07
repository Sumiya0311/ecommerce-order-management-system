from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse
)
from app.services.review_service import (
    create_review,
    get_product_reviews,
    update_review,
    delete_review
)

router = APIRouter(tags=["Reviews"])


@router.post(
    "/products/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def add_review(
    product_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return create_review(
        db,
        current_user.user_id,
        product_id,
        review_data
    )


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewResponse]
)
def list_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    return get_product_reviews(db, product_id)


@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse
)
def edit_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return update_review(
        db,
        current_user.user_id,
        review_id,
        review_data
    )


@router.delete(
    "/reviews/{review_id}"
)
def remove_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return delete_review(
        db,
        current_user.user_id,
        review_id
    )