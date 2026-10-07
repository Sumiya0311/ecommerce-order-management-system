from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)



@router.get("/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    total_orders = (
        db.query(func.count(Order.order_id))
        .filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        )
        .scalar()
    )

    paid_revenue = (
        db.query(func.coalesce(func.sum(Order.grand_total), 0))
        .filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date,
            Order.payment_status == "Paid"
        )
        .scalar()
    )

    refunds = (
        db.query(func.coalesce(func.sum(Order.grand_total), 0))
        .filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date,
            Order.payment_status == "Refunded"
        )
        .scalar()
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_orders": total_orders,
        "paid_revenue": float(paid_revenue),
        "refunds": float(refunds)
    }



@router.get("/orders-by-status")
def orders_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    results = (
        db.query(
            Order.status,
            func.count(Order.order_id).label("order_count")
        )
        .group_by(Order.status)
        .all()
    )

    return [
        {
            "status": status,
            "order_count": order_count
        }
        for status, order_count in results
    ]


# 3. Top 5 Products
@router.get("/top-products")
def top_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    results = (
        db.query(
            Product.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_quantity")
        )
        .join(OrderItem, Product.product_id == OrderItem.product_id)
        .join(Order, Order.order_id == OrderItem.order_id)
        .filter(Order.status != "Cancelled")
        .group_by(
            Product.product_id,
            Product.name
        )
        .order_by(
            func.sum(OrderItem.quantity).desc()
        )
        .limit(5)
        .all()
    )

    return [
        {
            "product_id": product_id,
            "product_name": name,
            "total_quantity": int(total_quantity)
        }
        for product_id, name, total_quantity in results
    ]



@router.get("/low-stock")
def low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))
):
    products = (
        db.query(Product)
        .filter(Product.stock_quantity < 5)
        .order_by(Product.stock_quantity.asc())
        .all()
    )

    return [
        {
            "product_id": product.product_id,
            "product_name": product.name,
            "stock_quantity": product.stock_quantity
        }
        for product in products
    ]