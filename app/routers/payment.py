from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import (
    CreatePaymentSessionRequest,
    CreatePaymentSessionResponse,
    PayOSWebhookPayload,
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
    Must be publicly accessible by PayOS.
    """
    _ensure_payos_config()

    raw = await request.body()
    signature = (
        request.headers.get("x-signature")
        or request.headers.get("x-payos-signature")
        or request.headers.get("x-webhook-signature")
        or request.headers.get("X-PayOS-Signature")
        or ""
    )
    if not _verify_signature(raw, signature):
        # Fallback: some integrations include signature in body alongside 'data'
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid signature")
        inline_sig = ""
        try:
            inline_sig = str(payload.get("signature") or "")
        except Exception:
            inline_sig = ""
        if inline_sig:
            # Verify HMAC over the 'data' object JSON (canonicalized)
            import json as _json

            try:
                data_section = payload.get("data", {})
                serialized = _json.dumps(
                    data_section, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                ).encode("utf-8")
                computed = hmac.new(
                    PAYOS_CHECKSUM_KEY.encode(), serialized, hashlib.sha256
                ).hexdigest()
                if not hmac.compare_digest(computed, inline_sig):
                    raise HTTPException(status_code=400, detail="Invalid signature")
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    body = payload.get("data") if isinstance(payload, dict) else None
    if not body:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Resolve order id from common fields (prefer orderCode)
    reference_id = (
        body.get("orderCode")
        or body.get("referenceId")
        or body.get("order_id")
        or body.get("orderId")
    )
    if not reference_id:
        raise HTTPException(status_code=400, detail="Missing order reference")

    order = db.get(Order, int(reference_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    status_text = str(body.get("status") or payload.get("status") or "").lower()
    code_text = str(body.get("code") or payload.get("code") or "")
    success_flag = body.get("success") if "success" in body else payload.get("success")

    # Treat completed on any of these conditions:
    # - success_flag is True
    # - code is "00" (common success code)
    # - status text indicates success
    if success_flag is True or code_text in ("00", "0") or status_text in ("success", "paid", "completed"):
        order.payment_status = PaymentStatus.COMPLETED
    # Treat failed on explicit failure indicators
    elif success_flag is False or status_text in ("failed", "cancelled", "canceled"):
        order.payment_status = PaymentStatus.FAILED
    # else ignore unexpected statuses to keep idempotency

    db.commit()
    return {"ok": True}

