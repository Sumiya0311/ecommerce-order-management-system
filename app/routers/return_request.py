from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.return_request import (
    ReturnCreate,
    ReturnReject,
    ReturnResponse
)
from app.services.return_service import (
    create_return,
    get_returns,
    approve_return,
    reject_return
)
from app.utils.email import send_email


router = APIRouter(
    tags=["Returns & Refunds"]
)




@router.post(
    "/orders/{order_id}/returns",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED
)
def request_return(
    order_id: int,
    return_data: ReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return create_return(
        db,
        current_user.user_id,
        order_id,
        return_data
    )




@router.get(
    "/returns",
    response_model=list[ReturnResponse]
)
def list_all_returns(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer", "Admin"))
):
    is_admin = current_user.role == "Admin"

    return get_returns(
        db,
        current_user.user_id,
        is_admin
    )




@router.put(
    "/returns/{return_id}/approve",
    response_model=ReturnResponse
)
def approve_return_request(
    return_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):

    return_request = approve_return(
        db,
        return_id
    )

    
    order = (
        db.query(Order)
        .filter(Order.order_id == return_request.order_id)
        .first()
    )

    if order:
        
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
                subject = (
                    f"Return Approved / Refund Processed - "
                    f"{order.order_number}"
                )

                body = f"""
Hello {user.name},

Your return request has been approved successfully.

Order Number: {order.order_number}
Order ID: {order.order_id}
Return ID: {return_request.return_id}

Return Status: {return_request.status}
Refund Amount: ₹{return_request.refund_amount:.2f}

The refund has been processed successfully.

Thank you for shopping with us!

E-Commerce Order Management System
"""

                background_tasks.add_task(
                    send_email,
                    user.email,
                    subject,
                    body
                )

    return return_request




@router.put(
    "/returns/{return_id}/reject",
    response_model=ReturnResponse
)
def reject_return_request(
    return_id: int,
    reject_data: ReturnReject,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    return_request = reject_return(
        db,
        return_id,
        reject_data
    )


    order = (
        db.query(Order)
        .filter(Order.order_id == return_request.order_id)
        .first()
    )

    if order:

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
                subject = (
                    f"Return Rejected - {order.order_number}"
                )

                body = f"""
Hello {user.name},

Your return request has been rejected.

Order Number: {order.order_number}
Order ID: {order.order_id}
Return ID: {return_request.return_id}

Return Status: {return_request.status}

Rejection Reason:
{return_request.rejection_reason}

If you have any questions, please contact our support team.

E-Commerce Order Management System
"""

                background_tasks.add_task(
                    send_email,
                    user.email,
                    subject,
                    body
                )

    return return_request