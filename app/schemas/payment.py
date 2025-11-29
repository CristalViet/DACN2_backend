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

