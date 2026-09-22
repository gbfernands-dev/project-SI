def test_openapi_exposes_versioned_contracts(client):
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "Loja Atlética Godzilla API"
    assert "/api/v1/products" in document["paths"]
    assert "/api/v1/orders/checkout" in document["paths"]
    assert "/api/v1/payments/webhook" in document["paths"]


def test_design_contract_is_valid_json(client):
    response = client.get("/promptcss.json")
    assert response.status_code == 200
    assert response.json()["tokens"]["colors"]["primary"] == "#BD4DFF"
