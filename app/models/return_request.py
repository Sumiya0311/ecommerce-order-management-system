from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
class ReturnRequest(Base):
    __tablename__ = "returns"

    return_id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        unique=True,
        nullable=False
    )

    reason = Column(String(500), nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="Requested"
    )

    refund_amount = Column(
        Float,
        nullable=True
    )

    rejection_reason = Column(
        String(500),
        nullable=True
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
        back_populates="returns"
    )