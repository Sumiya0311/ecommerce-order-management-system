from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)

    order_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.address_id"),
        nullable=False
    )

    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    delivery_charge = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="Pending"
    )

    payment_status = Column(
        String(20),
        nullable=False,
        default="Unpaid"
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

    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    address = relationship("Address")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    returns = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan"
    )