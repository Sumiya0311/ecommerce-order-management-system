from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


def create_payment(
    db: Session,
    user_id: int,
    order_id: int,
    payment_data: PaymentCreate
):
    order = (
        db.query(Order)
        .join(Order.customer)
        .filter(
            Order.order_id == order_id,
            Order.customer.has(user_id=user_id)
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Payment cannot be made for a cancelled order"
        )

    if order.payment_status == "Paid":
        raise HTTPException(
            status_code=400,
            detail="Order is already paid"
        )

    # COD does not require an online transaction
    if payment_data.payment_method == "COD":
        if payment_data.amount != order.grand_total:
            raise HTTPException(
                status_code=400,
                detail="Payment amount must match the order grand total"
            )

        payment = Payment(
            order_id=order.order_id,
            amount=order.grand_total,
            payment_method="COD",
            transaction_id=payment_data.transaction_id,
            status="Success"
        )

        db.add(payment)

        order.payment_status = "Paid"

        if order.status == "Pending":
            order.status = "Confirmed"

        db.commit()
        db.refresh(payment)

        return payment

    # Validate exact payment amount
    if payment_data.amount != order.grand_total:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must match the order grand total"
        )

    # Check duplicate transaction ID
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.transaction_id == payment_data.transaction_id
        )
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail="Transaction ID already exists"
        )

    payment = Payment(
        order_id=order.order_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_id=payment_data.transaction_id,
        status=payment_data.status
    )

    db.add(payment)

    # Successful payment
    if payment_data.status == "Success":
        order.payment_status = "Paid"

        if order.status == "Pending":
            order.status = "Confirmed"

    db.commit()
    db.refresh(payment)

    return payment


def get_payments(
    db: Session,
    user_id: int,
    order_id: int
):
    order = (
        db.query(Order)
        .filter(
            Order.order_id == order_id,
            Order.customer.has(user_id=user_id)
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .order_by(Payment.created_at.desc())
        .all()
    )