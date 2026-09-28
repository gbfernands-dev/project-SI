from app.config import get_settings


def test_openapi_exposes_versioned_contracts(client):
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "Loja Atlética Godzilla API"
    assert "/api/v1/products" in document["paths"]
    assert "/api/v1/orders/checkout" in document["paths"]
    assert "/api/v1/payments/webhook" in document["paths"]


def test_design_contract_is_valid_json(client):
    response = client.get("/promptcss.json")
    assert response.status_code == 200
    design = response.json()
    assert design["schema_version"] == "1.0.0"
    tokens = design["tokens"]
    assert tokens["colors"]["primary"] == "#BD4DFF"
    assert tokens["colors"]["background"] == "#0C0A10"
    assert tokens["typography"]["fontFamily"].startswith("Inter")
    assert tokens["radii"]["medium"] == "12px"
    assert design["color_system"]["primary"] == tokens["colors"]["primary"]
    assert design["css_system"]["variables"]["--color-primary"] == tokens["colors"]["primary"]


def test_logo_uses_the_static_assets_directory(client):
    settings = get_settings()
    expected_path = settings.static_dir / "assets" / "images" / "logo-atletica.png"

    assert settings.logo_path == expected_path
    response = client.get("/assets/logo")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
