from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(
        String(20),
        nullable=False
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
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

    order = relationship(
        "Order",
        back_populates="payments"
    )