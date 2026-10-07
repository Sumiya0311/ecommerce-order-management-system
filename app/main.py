from fastapi import FastAPI

from app.auth import auth
from app.routers import category, product, cart, address, order, payment, return_request, review, report


tags_metadata = [
    {
        "name": "Authentication",
        "description": "Authentication and user management"
    },
    {
        "name": "Categories",
        "description": "Category management"
    },
    {
        "name": "Products",
        "description": "Product management"
    },
    {
        "name": "Cart",
        "description": "Shopping cart management"
    },
    {
        "name": "Addresses",
        "description": "Customer address management"
    },
    {
        "name": "Orders",
        "description": "Order management"
    },
    {
        "name": "Payments",
        "description": "Payment processing"
    },
    {
        "name": "Returns & Refunds",
        "description": "Return and refund management"
    },
    {
        "name": "Reviews",
        "description": "Product review management"
    },
    {
        "name": "Reports",
        "description": "Sales and performance reports"
    }

]


app = FastAPI(
    title="E-Commerce Order Management System",
    description="E-Commerce Order Management API",
    version="1.0.0",
    openapi_tags=tags_metadata
)


app.include_router(auth.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(address.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(return_request.router)
app.include_router(review.router)
app.include_router(report.router)

@app.get("/")
def home():
    return {
        "message": "E-Commerce Order Management System API is running"
    }