from datetime import timedelta

from app.database import SessionLocal
from app.models import Session, now_utc
from tests.conftest import csrf_headers


def register(client):
    return client.post("/api/v1/auth/register", json={"name": "Maria Godzilla", "email": "maria@ugb.edu.br", "password": "segredo123"})


def test_customer_can_register_and_add_product_to_cart(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "customer"
    product = client.get("/api/v1/products").json()[0]
    added = client.post("/api/v1/cart/items", headers=csrf_headers(client), json={"variant_id": product["variants"][0]["id"], "quantity": 2})
    assert added.status_code == 201
    assert added.json()["total_cents"] == product["price_cents"] * 2


def test_example_administrator_email_is_accepted(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Administrador", "email": "admin@godzilla-ugb.com", "password": "segredo123"},
    )
    assert response.status_code == 201


def test_unknown_session_cookie_returns_unauthorized(client):
    client.cookies.set("godzilla_session", "invalid-session-token")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Sessão expirada."


def test_removed_or_expired_session_returns_unauthorized(client):
    register(client)
    db = SessionLocal()
    try:
        session = db.query(Session).one()
        session.expires_at = now_utc() - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    expired = client.get("/api/v1/auth/me")
    assert expired.status_code == 401

    db = SessionLocal()
    try:
        db.query(Session).delete()
        db.commit()
    finally:
        db.close()

    removed = client.get("/api/v1/auth/me")
    assert removed.status_code == 401


def test_checkout_and_mock_payment_reduce_stock_once(client):
    register(client)
    product = client.get("/api/v1/products").json()[0]
    variant = product["variants"][0]
    client.post("/api/v1/cart/items", headers=csrf_headers(client), json={"variant_id": variant["id"], "quantity": 1})
    checkout = client.post("/api/v1/orders/checkout", headers=csrf_headers(client))
    assert checkout.status_code == 200
    assert checkout.json()["checkout_url"].startswith("/pedido/")
    order_id = checkout.json()["order"]["id"]
    approved = client.post(f"/api/v1/payments/mock/orders/{order_id}/approve", headers=csrf_headers(client))
    assert approved.status_code == 200
    assert approved.json()["status"] == "paid"
    updated = client.get(f"/api/v1/products/{product['slug']}").json()
    assert next(item for item in updated["variants"] if item["id"] == variant["id"])["stock"] == variant["stock"] - 1
    again = client.post(f"/api/v1/payments/mock/orders/{order_id}/approve", headers=csrf_headers(client))
    assert again.status_code == 200
    updated_again = client.get(f"/api/v1/products/{product['slug']}").json()
    assert next(item for item in updated_again["variants"] if item["id"] == variant["id"])["stock"] == variant["stock"] - 1


def test_payment_approval_preserves_items_added_after_checkout(client):
    register(client)
    products = client.get("/api/v1/products").json()
    ordered_variant = products[0]["variants"][0]
    later_variant = products[1]["variants"][0]
    headers = csrf_headers(client)

    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": ordered_variant["id"], "quantity": 1})
    checkout = client.post("/api/v1/orders/checkout", headers=headers).json()
    assert client.get("/api/v1/cart").json()["items"] == []
    assert client.post("/api/v1/orders/checkout", headers=headers).status_code == 400
    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": later_variant["id"], "quantity": 1})

    response = client.post(
        f"/api/v1/payments/mock/orders/{checkout['order']['id']}/approve",
        headers=headers,
    )
    cart = client.get("/api/v1/cart").json()

    assert response.status_code == 200
    assert [item["variant"]["id"] for item in cart["items"]] == [later_variant["id"]]
