from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import (
    CreatePaymentSessionRequest,
    CreatePaymentSessionResponse,
    PayOSWebhookPayload,
    TestWebhookPayload,
)
from app.models.order import Order, PaymentStatus
from app.config import (
    PAYOS_CLIENT_ID,
    PAYOS_API_KEY,
    PAYOS_CHECKSUM_KEY,
    PAYOS_BASE_URL,
    FRONTEND_BASE_URL,
)
from payos import PayOS
from payos.types import CreatePaymentLinkRequest
import hmac
import hashlib
from decimal import Decimal
import logging
import json

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/payments", tags=["Payments"])


def _ensure_payos_config() -> None:
    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY or not PAYOS_CHECKSUM_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PayOS is not configured on the server",
        )


# Initialize PayOS client once
payos_client = None
if PAYOS_CLIENT_ID and PAYOS_API_KEY and PAYOS_CHECKSUM_KEY:
    try:
        payos_client = PayOS(PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY)
    except Exception:
        # Will be caught at request time by _ensure_payos_config if needed
        payos_client = None


@router.post("/session/", response_model=CreatePaymentSessionResponse)
async def create_payment_session(
    payload: CreatePaymentSessionRequest,
    db: Session = Depends(get_db),
):
    """
    Create a PayOS checkout session for an existing order (pending).
    """
    _ensure_payos_config()
    if payos_client is None:
        raise HTTPException(status_code=500, detail="PayOS client failed to initialize")

    order = db.get(Order, payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not pending")

    # Build request using official SDK
    # amount must be integer VND; orderCode must be an integer and unique
    total_amount_vnd = int(Decimal(str(order.total_amount)))
    return_url = f"{FRONTEND_BASE_URL}/payment/success?orderId={order.id}"
    cancel_url = f"{FRONTEND_BASE_URL}/payment/cancel?orderId={order.id}"

    try:
        payment_data = CreatePaymentLinkRequest(
            orderCode=order.id,
            amount=total_amount_vnd,
            description=f"Order #{order.id}",
            cancelUrl=cancel_url,
            returnUrl=return_url,
        )
        payment_link_response = payos_client.payment_requests.create(payment_data)
    except Exception as e:
        # Surface SDK error
        raise HTTPException(status_code=502, detail={"payos_error": str(e)})

    # Try multiple shapes from SDK return
    checkout_url = None
    try:
        # direct attribute
        checkout_url = (
            getattr(payment_link_response, "checkoutUrl", None)
            or getattr(payment_link_response, "checkout_url", None)
            or getattr(payment_link_response, "link", None)
        )
        # nested data attribute which may be a dict/object
        if not checkout_url:
            data_attr = getattr(payment_link_response, "data", None)
            if isinstance(data_attr, dict):
                checkout_url = (
                    data_attr.get("checkoutUrl")
                    or data_attr.get("link")
                    or data_attr.get("checkout_url")
                )
            else:
                checkout_url = (
                    getattr(data_attr, "checkoutUrl", None)
                    or getattr(data_attr, "checkout_url", None)
                    or getattr(data_attr, "link", None)
                )
        # dict-like return
        if not checkout_url and isinstance(payment_link_response, dict):
            checkout_url = (
                payment_link_response.get("checkoutUrl")
                or payment_link_response.get("link")
                or (payment_link_response.get("data") or {}).get("checkoutUrl")
                or (payment_link_response.get("data") or {}).get("link")
            )
    except Exception:
        checkout_url = None

    if not checkout_url:
        # include raw string form to help diagnose structure differences
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Invalid response from PayOS SDK",
                "payos_response": str(payment_link_response),
            },
        )

    return CreatePaymentSessionResponse(checkoutUrl=checkout_url, orderId=order.id)


def _verify_signature(body_bytes: bytes, signature: str) -> bool:
    """
    Verify HMAC-SHA256 signature sent by PayOS using checksum key.
    Header name may be 'x-signature' or 'x-payos-signature'.
    """
    if not signature:
        return False
    computed = hmac.new(PAYOS_CHECKSUM_KEY.encode(), body_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


@router.post("/webhook/")
async def payos_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Webhook to receive payment status updates from PayOS.
    Uses official PayOS SDK webhooks.verify for validation, per docs:
    https://payos.vn/docs/sdks/back-end/python
    """
    _ensure_payos_config()
    if payos_client is None:
        raise HTTPException(status_code=500, detail="PayOS client failed to initialize")

    # Read raw body once
    raw = await request.body()
    logger.info(f"Webhook received, body length: {len(raw)}")

    # Let PayOS SDK verify signature & parse payload
    try:
        webhook_data = payos_client.webhooks.verify(raw)
        # webhook_data is a typed object; log as dict/string for debugging
        logger.info(f"Verified PayOS webhook: {webhook_data}")
    except Exception as e:
        logger.error(f"Invalid PayOS webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Resolve order id from official field name `order_code`
    order_code = getattr(webhook_data, "order_code", None)
    if order_code is None:
        # Fallback: try common alternatives on data if present
        data = getattr(webhook_data, "data", None)
        order_code = None
        if isinstance(data, dict):
            order_code = (
                data.get("orderCode")
                or data.get("order_id")
                or data.get("orderId")
            )
    if order_code is None:
        logger.error(f"Missing order_code in webhook data: {webhook_data}")
        raise HTTPException(status_code=400, detail="Missing order reference")

    logger.info(f"Processing webhook for order: {order_code}")

    order = db.get(Order, int(order_code))
    if not order:
        # Trường hợp phổ biến khi PayOS chỉ gửi webhook test để kiểm tra URL,
        # orderCode có thể là số demo (ví dụ 123) không tồn tại trong hệ thống.
        # Để PayOS chấp nhận webhook URL, ta vẫn trả về 200 OK và chỉ log lại.
        logger.warning(
            f"Order not found for webhook order_code={order_code}. "
            "This may be a PayOS test/verification call. Ignoring update."
        )
        return {
            "ok": True,
            "ignored": True,
            "reason": "Order not found for given order_code",
        }

    # Extract status info according to PayOS docs
    code = getattr(webhook_data, "code", None)
    success = getattr(webhook_data, "success", None)

    # Some integrations put detailed status in data
    data = getattr(webhook_data, "data", None)
    status_text = ""
    if isinstance(data, dict):
        status_text = str(data.get("status") or "").lower()
        if code is None:
            code = data.get("code")

    logger.info(
        f"Webhook status info - code: {code}, success: {success}, status_text: {status_text}"
    )
    logger.info(f"Order {order.id} - Current status: {order.payment_status.value}")

    old_status = order.payment_status.value

    # Success rules per PayOS: success==True or code "00"
    if success is True or str(code) in ("00", "0") or status_text in (
        "success",
        "paid",
        "completed",
    ):
        order.payment_status = PaymentStatus.COMPLETED
        logger.info(f"Order {order.id} payment status updated: {old_status} -> completed")
    else:
        # Treat all non-success as failed, you can refine if needed
        order.payment_status = PaymentStatus.FAILED
        logger.info(f"Order {order.id} payment status updated: {old_status} -> failed")

    db.commit()
    db.refresh(order)
    logger.info(f"Order {order.id} final status: {order.payment_status.value}")

    return {"ok": True}


@router.post("/webhook/test/")
async def test_webhook(
    payload: TestWebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Test endpoint to simulate PayOS webhook call.
    This helps verify webhook logic without actual PayOS payment.
    
    Example:
    POST /payments/webhook/test/
    {
        "order_id": 16,
        "status": "PAID",
        "code": "00",
        "success": true
    }
    """
    logger.info(f"Test webhook called for order: {payload.order_id}")
    
    # Create a mock PayOS webhook payload
    mock_payload = {
        "data": {
            "orderCode": payload.order_id,
            "status": payload.status,
            "code": payload.code,
            "success": payload.success
        }
    }
    
    # Get order
    order = db.get(Order, payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order.payment_status.value
    logger.info(f"Order {order.id} - Current status: {old_status}")
    
    # Process status update (same logic as real webhook)
    status_text = payload.status.lower()
    code_text = payload.code
    
    if payload.success is True or code_text in ("00", "0") or status_text in ("success", "paid", "completed"):
        order.payment_status = PaymentStatus.COMPLETED
        logger.info(f"Order {order.id} payment status updated: {old_status} -> completed")
    elif payload.success is False or status_text in ("failed", "cancelled", "canceled"):
        order.payment_status = PaymentStatus.FAILED
        logger.info(f"Order {order.id} payment status updated: {old_status} -> failed")
    else:
        logger.warning(f"Order {order.id} - Unknown status, keeping current status")
    
    db.commit()
    db.refresh(order)
    
    return {
        "ok": True,
        "message": f"Test webhook processed successfully",
        "order_id": order.id,
        "old_status": old_status,
        "new_status": order.payment_status.value,
        "mock_payload": mock_payload
    }


@router.get("/webhook/logs/{order_id}")
async def get_webhook_info(
    order_id: int,
    db: Session = Depends(get_db),
):
    """
    Get current payment status of an order.
    Useful to check if webhook has updated the order status.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order_id": order.id,
        "payment_status": order.payment_status.value,
        "total_amount": float(order.total_amount),
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "message": "Check this endpoint after payment to verify webhook updated the status"
    }


@router.post("/webhook/manual-update/{order_id}")
async def manual_update_payment_status(
    order_id: int,
    status: str = "completed",  # "completed" or "failed"
    db: Session = Depends(get_db),
):
    """
    Manually update payment status for an order.
    Use this as a fallback when PayOS webhook doesn't work.
    
    Example:
    POST /payments/webhook/manual-update/17?status=completed
    POST /payments/webhook/manual-update/17?status=failed
    """
    logger.info(f"Manual payment status update requested for order {order_id} with status: {status}")
    
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order.payment_status.value
    logger.info(f"Order {order_id} - Current status: {old_status}")
    
    status_lower = status.lower()
    if status_lower in ("completed", "success", "paid"):
        order.payment_status = PaymentStatus.COMPLETED
        new_status = "completed"
    elif status_lower in ("failed", "cancelled", "canceled"):
        order.payment_status = PaymentStatus.FAILED
        new_status = "failed"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {status}. Use 'completed' or 'failed'"
        )
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order {order_id} payment status manually updated: {old_status} -> {new_status}")
    logger.info(f"Order {order_id} final status: {order.payment_status.value}")
    
    return {
        "ok": True,
        "message": f"Order {order_id} payment status updated manually",
        "order_id": order.id,
        "old_status": old_status,
        "new_status": order.payment_status.value
    }

