from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


def get_customer(db: Session, user_id: int):
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


def create_review(
    db: Session,
    user_id: int,
    product_id: int,
    review_data: ReviewCreate
):
    customer = get_customer(db, user_id)

    
    product = (
        db.query(Product)
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    delivered_order = (
        db.query(Order)
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .filter(
            Order.customer_id == customer.customer_id,
            Order.status == "Delivered",
            OrderItem.product_id == product_id
        )
        .first()
    )

    if not delivered_order:
        raise HTTPException(
            status_code=400,
            detail="You can review only products from delivered orders"
        )

    # One review per customer per product
    existing_review = (
        db.query(Review)
        .filter(
            Review.customer_id == customer.customer_id,
            Review.product_id == product_id
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=409,
            detail="You have already reviewed this product"
        )

    review = Review(
        product_id=product_id,
        customer_id=customer.customer_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_product_reviews(
    db: Session,
    product_id: int
):
    product = (
        db.query(Product)
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def update_review(
    db: Session,
    user_id: int,
    review_id: int,
    review_data: ReviewUpdate
):
    customer = get_customer(db, user_id)

    review = (
        db.query(Review)
        .filter(
            Review.review_id == review_id,
            Review.customer_id == customer.customer_id
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    review.rating = review_data.rating
    review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    return review


def delete_review(
    db: Session,
    user_id: int,
    review_id: int
):
    customer = get_customer(db, user_id)

    review = (
        db.query(Review)
        .filter(
            Review.review_id == review_id,
            Review.customer_id == customer.customer_id
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }