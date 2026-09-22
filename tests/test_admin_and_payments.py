from app.database import SessionLocal
from app.models import Role, User
from tests.conftest import csrf_headers


def register(client, email="admin@ugb.edu.br"):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Admin Godzilla", "email": email, "password": "segredo123"},
    )
    assert response.status_code == 201


def promote_to_admin(email="admin@ugb.edu.br"):
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).update({"role": Role.ADMIN})
        db.commit()
    finally:
        db.close()


def test_admin_can_manage_catalog_and_order_lifecycle(client):
    register(client)
    promote_to_admin()
    headers = csrf_headers(client)

    category = client.post("/api/v1/admin/categories", headers=headers, json={"name": "Eventos", "slug": "eventos"})
    assert category.status_code == 201
    created = client.post(
        "/api/v1/admin/products",
        headers=headers,
        json={
            "category_id": category.json()["id"],
            "name": "Regata Neon",
            "slug": "regata-neon",
            "description": "Produto de teste para o painel administrativo.",
            "price_cents": 4900,
        },
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    variant = client.post(
        f"/api/v1/admin/products/{product_id}/variants",
        headers=headers,
        json={"size": "M", "stock": 3},
    )
    assert variant.status_code == 201
    updated_variant = client.patch(
        f"/api/v1/admin/variants/{variant.json()['id']}",
        headers=headers,
        json={"size": "G", "stock": 4},
    )
    assert updated_variant.json()["size"] == "G"
    updated = client.patch(
        f"/api/v1/admin/products/{product_id}",
        headers=headers,
        json={"price_cents": 5500, "is_active": False},
    )
    assert updated.json()["price_cents"] == 5500
    assert any(item["id"] == product_id for item in client.get("/api/v1/admin/products").json())

    product = client.get("/api/v1/products").json()[0]
    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": product["variants"][0]["id"], "quantity": 1})
    order = client.post("/api/v1/orders/checkout", headers=headers).json()["order"]
    client.post(f"/api/v1/payments/mock/orders/{order['id']}/approve", headers=headers)
    orders = client.get("/api/v1/admin/orders").json()
    assert any(item["id"] == order["id"] for item in orders)
    available = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status", headers=headers, json={"status": "available"}
    )
    assert available.json()["status"] == "available"
    picked_up = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status", headers=headers, json={"status": "picked_up"}
    )
    assert picked_up.json()["status"] == "picked_up"


def test_catalog_filters_security_and_webhook(client, monkeypatch):
    register(client, "cliente@ugb.edu.br")
    headers = csrf_headers(client)
    products = client.get("/api/v1/products?q=camiseta&size=M&min_price=1&max_price=10000")
    assert products.status_code == 200
    assert products.json()[0]["name"] == "Camiseta Godzilla"
    assert client.post("/api/v1/cart/items", json={"variant_id": 1, "quantity": 1}).status_code == 403
    assert client.delete("/api/v1/cart/items/999", headers=headers).status_code == 404
    assert client.get("/api/v1/admin/orders").status_code == 403

    product = client.get("/api/v1/products").json()[0]
    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": product["variants"][0]["id"], "quantity": 1})
    order = client.post("/api/v1/orders/checkout", headers=headers).json()["order"]

    monkeypatch.setattr(
        "app.main.get_mercado_pago_payment",
        lambda payment_id: {"id": payment_id, "status": "approved", "external_reference": str(order["id"])},
    )
    response = client.post("/api/v1/payments/webhook", json={"data": {"id": "payment-123"}})
    assert response.status_code == 204
    assert client.get(f"/api/v1/orders/{order['id']}").json()["payment_status"] == "approved"
    assert client.post("/api/v1/payments/webhook", json={"data": {"id": "payment-123"}}).status_code == 204


def test_auth_validation_and_logout(client):
    assert client.post("/api/v1/auth/login", json={"email": "none@ugb.edu.br", "password": "nope"}).status_code == 401
    assert client.get("/api/v1/cart").status_code == 401
    register(client, "logout@ugb.edu.br")
    headers = csrf_headers(client)
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_static_frontend_and_logo_are_served(client):
    assert "Atlética Godzilla" in client.get("/").text
    assert client.get("/sobre").status_code == 200
    assert client.get("/assets/logo").headers["content-type"] == "image/png"
