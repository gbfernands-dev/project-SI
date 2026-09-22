import hashlib
import hmac
import json
import secrets
from pathlib import Path

import requests
from fastapi import HTTPException, UploadFile, status

from app.config import get_settings


def create_payment_preference(order_id: int, items: list[dict]) -> str:
    settings = get_settings()
    if not settings.mp_access_token:
        if settings.is_production:
            raise HTTPException(status_code=503, detail="Pagamento ainda não configurado.")
        return f"/pedido/{order_id}?modo=teste"
    payload = {
        "items": items,
        "external_reference": str(order_id),
        "notification_url": f"{settings.public_base_url}/api/v1/payments/webhook",
        "back_urls": {"success": f"{settings.public_base_url}/pedido/{order_id}", "failure": f"{settings.public_base_url}/pedido/{order_id}", "pending": f"{settings.public_base_url}/pedido/{order_id}"},
        "auto_return": "approved",
    }
    response = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={"Authorization": f"Bearer {settings.mp_access_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=15,
    )
    if not response.ok:
        raise HTTPException(status_code=502, detail="Não foi possível iniciar o pagamento.")
    body = response.json()
    return body.get("sandbox_init_point") or body["init_point"]


def get_mercado_pago_payment(payment_id: str) -> dict:
    settings = get_settings()
    response = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {settings.mp_access_token}"},
        timeout=15,
    )
    if not response.ok:
        raise HTTPException(status_code=502, detail="Não foi possível consultar o pagamento.")
    return response.json()


def verify_mercado_pago_signature(payload: dict, signature: str | None, request_id: str | None) -> bool:
    secret = get_settings().mp_webhook_secret
    if not secret:
        return not get_settings().is_production
    if not signature:
        return False
    parts = dict(item.split("=", 1) for item in signature.split(",") if "=" in item)
    timestamp, received = parts.get("ts"), parts.get("v1")
    data_id = str(payload.get("data", {}).get("id", ""))
    if not timestamp or not received or not data_id:
        return False
    manifest = f"id:{data_id};request-id:{request_id or ''};ts:{timestamp};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)


async def save_product_image(file: UploadFile) -> str:
    if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Envie PNG, JPEG ou WebP.")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="A imagem deve ter no máximo 5 MB.")
    suffix = Path(file.filename or "produto.png").suffix.lower() or ".png"
    filename = f"{secrets.token_urlsafe(16)}{suffix}"
    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_key:
        response = requests.post(
            f"{settings.supabase_url}/storage/v1/object/products/{filename}",
            headers={"Authorization": f"Bearer {settings.supabase_service_key}", "Content-Type": file.content_type},
            data=content,
            timeout=20,
        )
        if not response.ok:
            raise HTTPException(status_code=502, detail="Não foi possível salvar a imagem.")
        return f"{settings.supabase_url}/storage/v1/object/public/products/{filename}"
    upload_dir = settings.static_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / filename).write_bytes(content)
    return f"/static/uploads/{filename}"


def compact_json(value: dict) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
