from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


TAX_RATE = 0.18
DELIVERY_CHARGE = 50.0
FREE_DELIVERY_LIMIT = 500.0


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


def generate_order_number(db: Session):
    today = datetime.now().strftime("%Y%m%d")

    count = (
        db.query(Order)
        .filter(Order.order_number.like(f"ORD-{today}-%"))
        .count()
    )

    return f"ORD-{today}-{count + 1:04d}"


def create_order(
    db: Session,
    user_id: int,
    address_id: int
):
    customer = get_customer(db, user_id)

    address = (
        db.query(Address)
        .filter(
            Address.address_id == address_id,
            Address.customer_id == customer.customer_id
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer.customer_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.cart_id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )


    subtotal = 0.0

    for cart_item in cart_items:
        product = (
            db.query(Product)
            .filter(Product.product_id == cart_item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {cart_item.product_id} not found"
            )

        if not product.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Product '{product.name}' is inactive"
            )

        if cart_item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.name}'"
            )

        subtotal += cart_item.quantity * product.price

    tax_amount = round(subtotal * TAX_RATE, 2)


    if subtotal > FREE_DELIVERY_LIMIT:
        delivery_charge = 0.0
    else:
        delivery_charge = DELIVERY_CHARGE

    
    grand_total = round(
        subtotal + tax_amount + delivery_charge,
        2
    )

    try:
        order = Order(
            order_number=generate_order_number(db),
            customer_id=customer.customer_id,
            address_id=address.address_id,
            subtotal=round(subtotal, 2),
            tax_amount=tax_amount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            status="Pending",
            payment_status="Unpaid"
        )

        db.add(order)
        db.flush()
        for cart_item in cart_items:
            product = (
                db.query(Product)
                .filter(Product.product_id == cart_item.product_id)
                .first()
            )

            line_total = round(
                cart_item.quantity * product.price,
                2
            )

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                line_total=line_total
            )

            db.add(order_item)
            product.stock_quantity -= cart_item.quantity
        db.query(CartItem).filter(
            CartItem.cart_id == cart.cart_id
        ).delete()

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create order"
        )


def get_orders(db: Session, user_id: int):
    customer = get_customer(db, user_id)

    return (
        db.query(Order)
        .filter(Order.customer_id == customer.customer_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(
    db: Session,
    user_id: int,
    order_id: int
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

    return order


def cancel_order(
    db: Session,
    user_id: int,
    order_id: int
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

    if order.status not in ["Pending", "Confirmed"]:
        raise HTTPException(
            status_code=400,
            detail="Only Pending or Confirmed orders can be cancelled"
        )

    try:
        
        for item in order.items:
            product = (
                db.query(Product)
                .filter(Product.product_id == item.product_id)
                .first()
            )

            if product:
                product.stock_quantity += item.quantity

        order.status = "Cancelled"

        if order.payment_status == "Paid":
            order.payment_status = "Refunded"

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel order"
        )


def update_order_status(
    db: Session,
    order_id: int,
    new_status: str
):
    order = (
        db.query(Order)
        .filter(Order.order_id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_transitions = {
        "Pending": "Confirmed",
        "Confirmed": "Shipped",
        "Shipped": "Delivered"
    }

    expected_next_status = allowed_transitions.get(order.status)

    if expected_next_status != new_status:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status change. "
                f"Order is currently {order.status}."
            )
        )

    order.status = new_status

    db.commit()
    db.refresh(order)

    return order