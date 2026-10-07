from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cart_id = Column(
        Integer,
        ForeignKey("carts.cart_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    cart = relationship(
        "Cart",
        back_populates="items"
    )

    product = relationship("Product")