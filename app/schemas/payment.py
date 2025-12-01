from pydantic import BaseModel


class CreatePaymentSessionRequest(BaseModel):
    order_id: int


class CreatePaymentSessionResponse(BaseModel):
    checkoutUrl: str
    orderId: int


class PayOSWebhookPayload(BaseModel):
    # Minimal typing; structure may vary by PayOS version.
    # We primarily need a reference to order and a status field.
    data: dict


class TestWebhookPayload(BaseModel):
    """Model for testing webhook with PayOS-like payload"""
    order_id: int
    status: str = "PAID"  # PAID, PENDING, CANCELLED
    code: str = "00"  # 00 = success
    success: bool = True
