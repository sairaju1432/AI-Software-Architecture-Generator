import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import current_user
from app.core.config import get_settings
from app.models import User
from app.schemas.dto import CheckoutSessionRead, SubscriptionRead

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/subscription", response_model=SubscriptionRead)
def subscription(user: User = Depends(current_user)):
    return user.subscription


@router.post("/checkout", response_model=CheckoutSessionRead)
async def create_checkout_session(user: User = Depends(current_user)):
    settings = get_settings()
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        raise HTTPException(status_code=503, detail="Stripe checkout is not configured")

    payload = {
        "mode": "subscription",
        "customer_email": user.email,
        "line_items[0][price]": settings.stripe_price_id,
        "line_items[0][quantity]": "1",
        "success_url": settings.billing_success_url,
        "cancel_url": settings.billing_cancel_url,
        "metadata[user_id]": user.id,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://api.stripe.com/v1/checkout/sessions",
            data=payload,
            auth=(settings.stripe_secret_key, ""),
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Stripe checkout session creation failed")
    return CheckoutSessionRead(checkout_url=response.json()["url"])
