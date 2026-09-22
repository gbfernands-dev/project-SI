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
