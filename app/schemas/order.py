from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from app.models.order import PaymentStatus, ShipmentStatus


class OrderCreate(BaseModel):
    total_amount: Decimal
    payment_method: str | None = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    recipient_name: str | None = None
    address: str | None = None
    phone: str | None = None
    shipment_status: ShipmentStatus = ShipmentStatus.PENDING
    delivery_date: datetime | None = None
    shipping_method: str | None = None


class OrderUpdate(BaseModel):
    total_amount: Decimal | None = None
    payment_method: str | None = None
    payment_status: PaymentStatus | None = None
    recipient_name: str | None = None
    address: str | None = None
    phone: str | None = None
    shipment_status: ShipmentStatus | None = None
    delivery_date: datetime | None = None
    shipping_method: str | None = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: datetime
    total_amount: Decimal
    payment_method: str | None = None
    payment_status: PaymentStatus
    recipient_name: str | None = None
    address: str | None = None
    phone: str | None = None
    shipment_status: ShipmentStatus
    delivery_date: datetime | None = None
    shipping_method: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus


class ShipmentStatusUpdate(BaseModel):
    shipment_status: ShipmentStatus

