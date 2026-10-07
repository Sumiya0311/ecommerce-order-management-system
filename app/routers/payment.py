from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import create_payment, get_payments
from app.utils.email import send_email


router = APIRouter(
    prefix="/orders",
    tags=["Payments"]
)


@router.post(
    "/{order_id}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def pay_order(
    order_id: int,
    payment_data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    payment = create_payment(
        db,
        current_user.user_id,
        order_id,
        payment_data
    )
    if payment.status == "Success":

        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if order:

            subject = f"Payment Successful - Order #{order.order_id}"

            body = f"""
Hello {current_user.name},

Your payment has been successfully completed.

Order Number: {order.order_number}
Order ID: {order.order_id}

Payment Amount: ₹{payment.amount:.2f}
Payment Method: {payment.payment_method}
Transaction ID: {payment.transaction_id}
Payment Status: {payment.status}

Order Status: {order.status}

Thank you for your payment!

E-Commerce Order Management System
"""

            background_tasks.add_task(
                send_email,
                current_user.email,
                subject,
                body
            )

    return payment




@router.get(
    "/{order_id}/payments",
    response_model=list[PaymentResponse]
)
def list_payments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_payments(
        db,
        current_user.user_id,
        order_id
    )