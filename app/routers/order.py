from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)
from app.services.order_service import (
    create_order,
    get_orders,
    get_order,
    cancel_order,
    update_order_status
)
from app.utils.email import send_email


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# PLACE ORDER
@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def place_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    order = create_order(
        db,
        current_user.user_id,
        order_data.address_id
    )

    subject = f"Order Placed Successfully - {order.order_number}"

    body = f"""
Hello {current_user.name},

Your order has been placed successfully.

Order Number: {order.order_number}
Order ID: {order.order_id}
Grand Total: ₹{order.grand_total:.2f}
Order Status: {order.status}
Payment Status: {order.payment_status}

Thank you for shopping with us!

E-Commerce Order Management System
"""

    background_tasks.add_task(
        send_email,
        current_user.email,
        subject,
        body
    )

    return order

# GET CUSTOMER ORDERS

@router.get(
    "",
    response_model=list[OrderResponse]
)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_orders(
        db,
        current_user.user_id
    )

# GET SINGLE ORDER

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_single_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_order(
        db,
        current_user.user_id,
        order_id
    )

# CANCEL ORDER

@router.put(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
def cancel_customer_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    order = cancel_order(
        db,
        current_user.user_id,
        order_id
    )

    subject = f"Order Cancelled - {order.order_number}"

    body = f"""
Hello {current_user.name},

Your order has been cancelled successfully.

Order Number: {order.order_number}
Order ID: {order.order_id}
Grand Total: ₹{order.grand_total:.2f}
Order Status: {order.status}
Payment Status: {order.payment_status}

If you have any questions, please contact our support team.

E-Commerce Order Management System
"""

    background_tasks.add_task(
        send_email,
        current_user.email,
        subject,
        body
    )

    return order


# UPDATE ORDER STATUS - ADMIN

@router.put(
    "/{order_id}/status",
    response_model=OrderResponse
)
def change_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    order = update_order_status(
        db,
        order_id,
        status_data.status
    )

    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == order.customer_id)
        .first()
    )

    if customer:
        user = (
            db.query(User)
            .filter(User.user_id == customer.user_id)
            .first()
        )

        if user:

            

            if order.status == "Shipped":

                subject = f"Order Shipped - {order.order_number}"

                body = f"""
Hello {user.name},

Your order has been shipped successfully.

Order Number: {order.order_number}
Order ID: {order.order_id}
Order Status: {order.status}
Grand Total: ₹{order.grand_total:.2f}

Your order is on the way!

E-Commerce Order Management System
"""

                background_tasks.add_task(
                    send_email,
                    user.email,
                    subject,
                    body
                )


            elif order.status == "Delivered":

                subject = f"Order Delivered - {order.order_number}"

                body = f"""
Hello {user.name},

Your order has been delivered successfully.

Order Number: {order.order_number}
Order ID: {order.order_id}
Order Status: {order.status}
Grand Total: ₹{order.grand_total:.2f}

Thank you for shopping with us!

E-Commerce Order Management System
"""

                background_tasks.add_task(
                    send_email,
                    user.email,
                    subject,
                    body
                )

    return order