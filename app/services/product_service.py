from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, product_data: ProductCreate):
    category = (
        db.query(Category)
        .filter(
            Category.category_id == product_data.category_id,
            Category.is_active == True
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found or inactive"
        )

    existing_product = (
        db.query(Product)
        .filter(Product.sku == product_data.sku)
        .first()
    )

    if existing_product:
        raise HTTPException(
            status_code=409,
            detail="SKU already exists"
        )

    product = Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        category_id=product_data.category_id,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_products(
    db: Session,
    name: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 10
):
    query = (
        db.query(Product)
        .filter(Product.is_active == True)
    )

    if name:
        query = query.filter(
            Product.name.ilike(f"%{name}%")
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if in_stock is True:
        query = query.filter(
            Product.stock_quantity > 0
        )
    elif in_stock is False:
        query = query.filter(
            Product.stock_quantity == 0
        )

    if sort_by == "price":
        sort_column = Product.price
    else:
        sort_column = Product.created_at

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id,
            Product.is_active == True
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate
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

    category = (
        db.query(Category)
        .filter(
            Category.category_id == product_data.category_id,
            Category.is_active == True
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found or inactive"
        )

    existing_product = (
        db.query(Product)
        .filter(
            Product.sku == product_data.sku,
            Product.product_id != product_id
        )
        .first()
    )

    if existing_product:
        raise HTTPException(
            status_code=409,
            detail="SKU already exists"
        )

    product.name = product_data.name
    product.sku = product_data.sku
    product.description = product_data.description
    product.category_id = product_data.category_id
    product.price = product_data.price
    product.stock_quantity = product_data.stock_quantity
    product.is_active = product_data.is_active

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int):
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

    product.is_active = False

    db.commit()

    return {
        "message": "Product deleted successfully"
    }