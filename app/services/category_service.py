from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_data: CategoryCreate):
    existing_category = (
        db.query(Category)
        .filter(Category.name == category_data.name)
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    category = Category(
        name=category_data.name,
        is_active=True
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_categories(db: Session):
    return db.query(Category).all()


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate
):
    category = (
        db.query(Category)
        .filter(Category.category_id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_category = (
        db.query(Category)
        .filter(
            Category.name == category_data.name,
            Category.category_id != category_id
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    category.name = category_data.name

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category_id: int):
    category = (
        db.query(Category)
        .filter(Category.category_id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    active_products = (
        db.query(Product)
        .filter(
            Product.category_id == category_id,
            Product.is_active == True
        )
        .count()
    )

    if active_products > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with active products"
        )

    category.is_active = False

    db.commit()

    return {"message": "Category deleted successfully"}