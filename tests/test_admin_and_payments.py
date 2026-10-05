from app.bootstrap import provision_admin_accounts
from app.catalog import synchronize_catalog
from app.database import SessionLocal
from app.models import AdminScope, Role, User
from app.security import verify_password
from tests.conftest import csrf_headers


def register(client, email="admin@ugb.edu.br"):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Admin Godzilla", "email": email, "password": "segredo123"},
    )
    assert response.status_code == 201


def promote_to_admin(email="admin@ugb.edu.br", scope=AdminScope.SITE):
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).update({"role": Role.ADMIN, "admin_scope": scope})
        db.commit()
    finally:
        db.close()


def test_bootstrap_provisions_site_and_athletics_administrators():
    environment = {
        "ADMIN_EMAIL": "admin@example.com",
        "ADMIN_PASSWORD": "site-password",
        "ATHLETICS_ADMIN_EMAIL": "athletics@example.com",
        "ATHLETICS_ADMIN_PASSWORD": "athletics-password",
    }
    db = SessionLocal()
    try:
        db.add(User(name="Conta existente", email="athletics@example.com", password_hash="old", role=Role.CUSTOMER))
        db.commit()

        provision_admin_accounts(db, environment)

        admins = db.query(User).filter(User.email.in_({"admin@example.com", "athletics@example.com"})).all()
        assert {user.email for user in admins} == {"admin@example.com", "athletics@example.com"}
        assert all(user.role == Role.ADMIN for user in admins)
        assert {user.email: user.admin_scope for user in admins} == {
            "admin@example.com": AdminScope.SITE,
            "athletics@example.com": AdminScope.ATHLETICS,
        }
        passwords = {"admin@example.com": "site-password", "athletics@example.com": "athletics-password"}
        assert all(verify_password(passwords[user.email], user.password_hash) for user in admins)
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
    deleted = client.delete(f"/api/v1/admin/products/{product_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json() == {"message": "Produto excluído do catálogo."}
    deleted_product = next(item for item in client.get("/api/v1/admin/products").json() if item["id"] == product_id)
    assert deleted_product["is_active"] is False
    assert all(item["id"] != product_id for item in client.get("/api/v1/products").json())

    product = client.get("/api/v1/products").json()[0]
    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": product["variants"][0]["id"], "quantity": 1})
    order = client.post("/api/v1/orders/checkout", headers=headers).json()["order"]
    client.post(f"/api/v1/payments/mock/orders/{order['id']}/approve", headers=headers)
    orders = client.get("/api/v1/admin/orders").json()
    admin_order = next(item for item in orders if item["id"] == order["id"])
    assert admin_order["user"] == {
        "id": admin_order["user"]["id"],
        "name": "Admin Godzilla",
        "email": "admin@ugb.edu.br",
    }
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
    assert {product["name"] for product in products.json()} == {
        "Camiseta Essential Godzilla",
        "Camiseta Oversized Godzilla Core",
    }
    assert client.post("/api/v1/cart/items", json={"variant_id": 1, "quantity": 1}).status_code == 403
    assert client.delete("/api/v1/cart/items/999", headers=headers).status_code == 404
    assert client.get("/api/v1/admin/orders").status_code == 403

    product = client.get("/api/v1/products").json()[0]
    client.post("/api/v1/cart/items", headers=headers, json={"variant_id": product["variants"][0]["id"], "quantity": 1})
    order = client.post("/api/v1/orders/checkout", headers=headers).json()["order"]

    monkeypatch.setattr(
        "app.main.get_mercado_pago_payment",
        lambda payment_id: {
            "id": payment_id,
            "status": "approved",
            "external_reference": str(order["id"]),
            "transaction_amount": 0.01 if payment_id == "payment-invalid" else order["total_cents"] / 100,
            "currency_id": "BRL",
            "live_mode": False,
        },
    )
    invalid = client.post(
        "/api/v1/payments/webhook?data.id=payment-invalid", json={"data": {"id": "payment-invalid"}}
    )
    assert invalid.status_code == 200
    assert client.get(f"/api/v1/orders/{order['id']}").json()["payment_status"] == "pending"
    response = client.post("/api/v1/payments/webhook?data.id=payment-123", json={"data": {"id": "payment-123"}})
    assert response.status_code == 200
    assert client.get(f"/api/v1/orders/{order['id']}").json()["payment_status"] == "approved"
    assert client.post(
        "/api/v1/payments/webhook?data.id=payment-123", json={"data": {"id": "payment-123"}}
    ).status_code == 200


def test_admin_orders_identify_different_customers_without_changing_customer_contract(client):
    order_ids = []
    customers = [
        ("Cliente Um", "cliente1@ugb.edu.br"),
        ("Cliente Dois", "cliente2@ugb.edu.br"),
    ]
    for name, email in customers:
        response = client.post(
            "/api/v1/auth/register",
            json={"name": name, "email": email, "password": "segredo123"},
        )
        assert response.status_code == 201
        headers = csrf_headers(client)
        product = client.get("/api/v1/products").json()[0]
        client.post(
            "/api/v1/cart/items",
            headers=headers,
            json={"variant_id": product["variants"][0]["id"], "quantity": 1},
        )
        order_ids.append(client.post("/api/v1/orders/checkout", headers=headers).json()["order"]["id"])
        if email == customers[0][1]:
            client.post("/api/v1/auth/logout", headers=headers)

    promote_to_admin(customers[1][1])
    customer_orders = client.get("/api/v1/orders").json()
    assert all("user" not in order for order in customer_orders)

    admin_orders = client.get("/api/v1/admin/orders").json()
    customers_by_order = {order["id"]: order["user"] for order in admin_orders}
    assert customers_by_order[order_ids[0]]["name"] == customers[0][0]
    assert customers_by_order[order_ids[0]]["email"] == customers[0][1]
    assert customers_by_order[order_ids[1]]["name"] == customers[1][0]
    assert customers_by_order[order_ids[1]]["email"] == customers[1][1]


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


def test_site_and_athletics_admins_have_distinct_permissions(client):
    register_response = client.post(
        "/api/v1/auth/register",
        headers={"CF-IPCountry": "BR", "CF-IPCity": "Volta Redonda"},
        json={"name": "Admin Site", "email": "admin@admin.com", "password": "segredo123"},
    )
    assert register_response.status_code == 201
    promote_to_admin("admin@admin.com", AdminScope.SITE)
    client.post("/api/v1/auth/logout", headers=csrf_headers(client))
    login = client.post(
        "/api/v1/auth/login",
        headers={"CF-IPCountry": "BR", "CF-IPCity": "Volta Redonda"},
        json={"email": "admin@admin.com", "password": "segredo123"},
    )
    site_headers = {"X-CSRF-Token": login.json()["csrf_token"]}
    assert login.json()["user"]["admin_scope"] == "site"

    overview = client.get("/api/v1/admin/overview")
    assert overview.status_code == 200
    assert overview.json()["health"]["database"] == "ok"
    assert overview.json()["integrations"]["mercado_pago"]["access_token_configured"] is False
    assert "APP_USR" not in overview.text
    users = client.get("/api/v1/admin/users")
    assert users.status_code == 200
    site_user = next(user for user in users.json() if user["email"] == "admin@admin.com")
    assert site_user["last_login_ip"] == "testclient"
    assert site_user["last_login_location"] == "Volta Redonda, BR"

    assert client.post("/api/v1/auth/logout", headers=site_headers).status_code == 200
    register(client, "atletica@atletica.com")
    promote_to_admin("atletica@atletica.com", AdminScope.ATHLETICS)
    assert client.post("/api/v1/auth/logout", headers=csrf_headers(client)).status_code == 200
    athletics = client.post(
        "/api/v1/auth/login",
        json={"email": "atletica@atletica.com", "password": "segredo123"},
    ).json()
    athletics_headers = {"X-CSRF-Token": athletics["csrf_token"]}
    assert athletics["user"]["admin_scope"] == "athletics"
    assert client.get("/api/v1/admin/products").status_code == 200
    assert client.get("/api/v1/admin/overview").status_code == 403
    assert client.get("/api/v1/admin/users").status_code == 403
    assert client.get("/api/v1/admin/orders").status_code == 403

    product = client.get("/api/v1/admin/products").json()[0]
    update = client.patch(
        f"/api/v1/admin/products/{product['id']}",
        headers=athletics_headers,
        json={"name": f"{product['name']} editado"},
    )
    assert update.status_code == 200
    assert update.json()["name"].endswith("editado")
    assert client.delete(f"/api/v1/admin/products/{product['id']}", headers=athletics_headers).status_code == 200
    db = SessionLocal()
    try:
        synchronize_catalog(db)
    finally:
        db.close()

    persisted = next(item for item in client.get("/api/v1/admin/products").json() if item["id"] == product["id"])
    assert persisted["name"].endswith("editado")
    assert persisted["is_active"] is False
