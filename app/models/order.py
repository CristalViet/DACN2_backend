from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, String, Enum
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(100), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    recipient_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    shipment_status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    shipping_method = Column(String(100), nullable=True)

    user = relationship("User", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")


