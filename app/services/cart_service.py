from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate


def get_or_create_cart(db: Session, user_id: int):
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

    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer.customer_id)
        .first()
    )

    if not cart:
        cart = Cart(customer_id=customer.customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def get_cart(db: Session, user_id: int):
    cart = get_or_create_cart(db, user_id)

    items = []

    for item in cart.items:
        if not item.product.is_active:
            continue

        line_total = item.quantity * item.product.price

        items.append({
            "cart_item_id": item.cart_item_id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price,
            "line_total": line_total
        })

    subtotal = sum(item["line_total"] for item in items)

    return {
        "cart_id": cart.cart_id,
        "items": items,
        "subtotal": subtotal
    }


def add_cart_item(
    db: Session,
    user_id: int,
    item_data: CartItemCreate
):
    cart = get_or_create_cart(db, user_id)

    product = (
        db.query(Product)
        .filter(Product.product_id == item_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive products cannot be added to cart"
        )

    if item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.cart_id,
            CartItem.product_id == product.product_id
        )
        .first()
    )

    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity

        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail="Requested quantity exceeds available stock"
            )

        existing_item.quantity = new_quantity

    else:
        cart_item = CartItem(
            cart_id=cart.cart_id,
            product_id=product.product_id,
            quantity=item_data.quantity
        )

        db.add(cart_item)

    db.commit()

    return get_cart(db, user_id)


def update_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
    item_data: CartItemUpdate
):
    cart = get_or_create_cart(db, user_id)

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_item_id == cart_item_id,
            CartItem.cart_id == cart.cart_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = (
        db.query(Product)
        .filter(Product.product_id == cart_item.product_id)
        .first()
    )

    if not product or not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Product is not available"
        )

    if item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart_item.quantity = item_data.quantity

    db.commit()

    return get_cart(db, user_id)


def delete_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int
):
    cart = get_or_create_cart(db, user_id)

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_item_id == cart_item_id,
            CartItem.cart_id == cart.cart_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return get_cart(db, user_id)


def clear_cart(db: Session, user_id: int):
    cart = get_or_create_cart(db, user_id)

    db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id
    ).delete()

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }