from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.models.product import Product
from app.schemas.return_request import ReturnCreate, ReturnReject


def get_customer(db: Session, user_id: int):
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    return customer


def create_return(
    db: Session,
    user_id: int,
    order_id: int,
    return_data: ReturnCreate
):
    customer = get_customer(db, user_id)

    order = (
        db.query(Order)
        .filter(
            Order.order_id == order_id,
            Order.customer_id == customer.customer_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != "Delivered":
        raise HTTPException(
            status_code=400,
            detail="Returns are allowed only for delivered orders"
        )

    # Order.updated_at represents the latest status update.
    # Since the order must be Delivered, this is used as the delivery time.
    if order.updated_at:
        if datetime.utcnow() - order.updated_at > timedelta(days=7):
            raise HTTPException(
                status_code=400,
                detail="Return request must be made within 7 days of delivery"
            )

    existing_return = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.order_id == order_id)
        .first()
    )

    if existing_return:
        raise HTTPException(
            status_code=409,
            detail="A return request already exists for this order"
        )

    return_request = ReturnRequest(
        order_id=order.order_id,
        reason=return_data.reason,
        status="Requested",
        refund_amount=None,
        rejection_reason=None
    )

    db.add(return_request)
    db.commit()
    db.refresh(return_request)

    return return_request


def get_returns(
    db: Session,
    user_id: int,
    is_admin: bool = False
):
    if is_admin:
        return (
            db.query(ReturnRequest)
            .order_by(ReturnRequest.created_at.desc())
            .all()
        )

    customer = get_customer(db, user_id)

    return (
        db.query(ReturnRequest)
        .join(Order)
        .filter(
            Order.customer_id == customer.customer_id
        )
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )


def approve_return(
    db: Session,
    return_id: int
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.return_id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if return_request.status != "Requested":
        raise HTTPException(
            status_code=400,
            detail="Only requested returns can be approved"
        )

    order = return_request.order

    try:
        # Restore product stock
        for order_item in order.items:
            product = (
                db.query(Product)
                .filter(
                    Product.product_id == order_item.product_id
                )
                .first()
            )

            if product:
                product.stock_quantity += order_item.quantity

        # Full order amount is refunded
        return_request.refund_amount = order.grand_total
        return_request.status = "Refunded"

        # Update order payment status
        order.payment_status = "Refunded"

        db.commit()
        db.refresh(return_request)

        return return_request

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to approve return and process refund"
        )


def reject_return(
    db: Session,
    return_id: int,
    reject_data: ReturnReject
):
    return_request = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.return_id == return_id)
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if return_request.status != "Requested":
        raise HTTPException(
            status_code=400,
            detail="Only requested returns can be rejected"
        )

    return_request.status = "Rejected"
    return_request.rejection_reason = reject_data.rejection_reason

    db.commit()
    db.refresh(return_request)

    return return_request