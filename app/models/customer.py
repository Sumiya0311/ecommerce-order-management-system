from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
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

    user = relationship("User")

    cart = relationship(
        "Cart",
        back_populates="customer",
        uselist=False
    )

    addresses = relationship(
        "Address",
        back_populates="customer"
    )

    orders = relationship(
        "Order",
        back_populates="customer"
    )